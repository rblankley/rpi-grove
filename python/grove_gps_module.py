#!/usr/bin/env python

from threading import Lock, Thread

import re
import serial
import sys
import time

# =================================================================================================
class Grove_GPS_Serial( Thread ):
    """! Thread object that manages serial communication """

    DEBUG = False
    POLL_TIME = 0.05

    GPGGA=["$GPGGA",
        "[0-9]{6}\.[0-9]{3}",                       # timestamp hhmmss.sss
        "[0-9]+\.[0-9]{2,}",                        # latitude of position ddmm.mmmmm
        "[NS]{1}",                                  # North or South
        "[0-9]+\.[0-9]{2,}",                        # longitude of position ddmm.mmmmm
        "[EW]{1}",                                  # East or West
        "[0123]",                                   # GPS Position Indicator; 0 Fix not available or invalid, 1 GPS SPS Mode, fix valid, 2 Differential GPS, SPS Mode, fix valid, 3 GPS PPS Mode, fix valid 
        "[0-9]{1,2}",                               # Number of satellites
        "[0-9]+\.[0-9]*",                           # horizontal dilution of precision x.x
        "[0-9]+\.[0-9]*",                           # altitude x.x (meters)
        "\w",                                       # altitude units
        "-?[0-9]+\.[0-9]*",                         # geoids separation x.x (meters)
        "\w",                                       # geoids separation units
        ]

    GPRMC=["$GPRMC",
        "[0-9]{6}\.[0-9]{3}",                       # uts timestamp hhmmss.sss
        "[AV]{1}",                                  # status; A data valid, V data not valid
        "[0-9]+\.[0-9]{2,}",                        # latitude of position ddmm.mmmmm
        "[NS]{1}",                                  # North or South
        "[0-9]+\.[0-9]{2,}",                        # longitude of position ddmm.mmmmm
        "[EW]{1}",                                  # East or West
        "[0-9]+\.[0-9]*",                           # speed over ground (knots)
        "[0-9]+\.[0-9]*",                           # measured heading true (degrees)
        "[0-9]{6}",                                 # date ddmmyy
        ]

    GPVTG=["$GPVTG",
        "[0-9]+\.[0-9]*",                           # measured heading true (degrees)
        "[T]{1}",                                   # True
        "[0-9]+\.[0-9]*",                           # measured heading magnetic (degrees)
        "[M]{1}",                                   # Magnetic
        "[0-9]+\.[0-9]*",                           # measured horizontal speed (knots)
        "[N]{1}",                                   # Knots
        "[0-9]+\.[0-9]*",                           # measured heading magnetic (kilometers)
        "[K]{1}",                                   # Kilometers / hr
        ]

    KNOTS_TO_KM_PER_HR = 1.852

    # ---------------------------------------------------------------------------------------------
    def __init__( self, port, baud, timeout ):
        """! Initialize Class
        @param port  serial device
        @param baud  baud rate
        @param timeout  timeout
        """
        super( Grove_GPS_Serial, self ).__init__()

        self.__ser = serial.Serial( port, baud, timeout=timeout )
        self.__ser.flush()

        self.__lock = Lock()

        self.__quit = False

        # GGA Global positioning system fixed data
        self.__gga = [] # contains compiled regex

        for p in self.GPGGA:
            self.__gga.append( re.compile( p ) ) # compile regex once to use later

        # RMC Recommended Minimum Specific GNSS Data
        self.__rmc = [] # contains compiled regex

        for p in self.GPRMC:
            self.__rmc.append( re.compile( p ) ) # compile regex once to use later

        # VTG Course Over Ground and Ground Speed
        self.__vtg = [] # contains compiled regex

        for p in self.GPVTG:
            self.__vtg.append( re.compile( p ) ) # compile regex once to use later

        # default values
        self.__timestamp = 0.0
        self.__latitude = 0.0
        self.__longitude = 0.0
        self.__pos = 0
        self.__satellites = 0
        self.__hdop = 0.0
        self.__altitude = 0.0
        self.__geoids = 0.0

        self.__heading = 0.0
        self.__velocity = 0.0

        self.__date = 0

    # ---------------------------------------------------------------------------------------------
    def __debug( self, s ):
        """! Print debug statement
        @param s  statement
        """
        if ( self.DEBUG ):
            print( s )

    # ---------------------------------------------------------------------------------------------
    def __validate_expression( self, ident, line, exp ):
        """! Runs regex validation on a line
        @param ident  identifier
        @param line  line to parse
        @param exp  regex
        @return  @c True if everything is all right, @c False if the sentence is mangled
        """
        if ( not line.startswith( ident ) ):
            return False

        '''
        # sometimes multiple GPS data packets come into the stream... take the data only after the last ident is seen
        i = line.rindex( ident )
        line = line[i:]
        '''

        lines = line.split( "," )
        self.__debug( lines )

        if ( len(lines) < len(exp) ):
            self.__debug( "Failed: wrong number of parameters " )
            self.__debug( exp )
            return False

        for i in range( 1, len(exp) ):
            if ( not exp[i].match( lines[i] ) ):
                self.__debug( "Failed: wrong format on parameter %d" % i )
                return False
            else:
                self.__debug( "Passed %d" % i )

        return True

    # ---------------------------------------------------------------------------------------------
    def stop( self ):
        """! Stop thread and wait for completion """
        self.__lock.acquire()
        self.__quit = True
        self.__lock.release()

        self.join()

    # ---------------------------------------------------------------------------------------------
    def run( self ):
        """! Thread run method """
        
        buffer = []

        while ( True ):
            self.__lock.acquire()

            try:
                
                # check to exit thread
                if ( self.__quit ):
                    self.__quit = False
                    break

                # read serial port
                pending = self.__ser.inWaiting()

                if ( 0 != pending ):
                    for c in self.__ser.read( pending ):
                        ch = c.decode( 'utf-8' )

                        if ( ch != '\n' ):
                            buffer.append( ch )

                        # process buffer when we see line feed
                        else:
                            line = ''.join( str(v) for v in buffer )
                            line.strip()

                            buffer = []

                            if ( len( line ) ):
                                self.__debug( line )

                                # gga
                                if ( self.__validate_expression( self.GPGGA[0], line, self.__gga ) ):
                                    '''
                                    # sometimes multiple GPS data packets come into the stream... take the data only after the last ident is seen
                                    i = line.rindex( ident )
                                    line = line[i:]
                                    '''
                                    lines = line.split( "," )

                                    self.__timestamp = float( lines[1] )

                                    lat = float( lines[2] )
                                    NS = lines[3]

                                    self.__latitude = lat // 100 + lat % 100 / 60
                                    if ( NS == "S" ):
                                        self.__latitude *= -1.0

                                    lon = float( lines[4] )
                                    EW = lines[5]

                                    self.__longitude = lon // 100 + lon % 100 / 60
                                    if ( EW == "W" ):
                                        self.__longitude = -self.__longitude

                                    self.__pos = int( lines[6] )
                                    self.__satellites = int( lines[7] )
                                    self.__hdop = float( lines[8] )
                                    self.__altitude = float( lines[9] )
                                    self.__geoids = float( lines[11] )

                                # rmc
                                elif ( self.__validate_expression( self.GPRMC[0], line, self.__rmc ) ):
                                    '''
                                    # sometimes multiple GPS data packets come into the stream... take the data only after the last ident is seen
                                    i = line.rindex( ident )
                                    line = line[i:]
                                    '''
                                    lines = line.split( "," )

                                    if ( 'A' != lines[2] ):
                                        self.__debug( "RMC data not valid" )

                                    else:
                                        self.__velocity = float( lines[7] ) * self.KNOTS_TO_KM_PER_HR
                                        self.__heading = float( lines[8] )
                                        self.__date = float( lines[9] )

                                # vtg
                                elif ( self.__validate_expression( self.GPVTG[0], line, self.__vtg ) ):
                                    '''
                                    # sometimes multiple GPS data packets come into the stream... take the data only after the last ident is seen
                                    i = line.rindex( ident )
                                    line = line[i:]
                                    '''
                                    lines = line.split( "," )

                                    self.__heading = float( lines[1] )
                                    self.__velocity = float( lines[5] ) * self.KNOTS_TO_KM_PER_HR

            finally:
                self.__lock.release()

            time.sleep( self.POLL_TIME )


    # ---------------------------------------------------------------------------------------------
    def utc( self ):
        """! Retrieve UTC Time
        @return  utc time (hhmmss)
        """
        self.__lock.acquire()
        result = int( self.__timestamp )
        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def date( self ):
        """! Retrieve UTC Date
        @return  date (ddmmyy)
        """
        self.__lock.acquire()
        result = int( self.__date )
        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def location( self ):
        """! Retrieve current location
        @return  location as (latitude, longitude)
        """
        self.__lock.acquire()
        result = (self.__latitude, self.__longitude)
        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def link( self ):
        """! Check for satellite link
        @return  @c True if link exists, @c False otherwise
        """
        self.__lock.acquire()

        if ( 0 == self.__pos ):
            result = False
        else:
            result = True

        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def altitude( self ):
        """! Retrieve current altitude
        @return  altitude (meters)
        """
        self.__lock.acquire()
        result = self.__altitude
        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def hdop( self ):
        """! Retrieve horizontal dilution of precision
        @return  hdop
        """
        self.__lock.acquire()
        result = self.__hdop
        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def satellitesInView( self ):
        """! Retrieve number of satellites in view
        @return  number of satellites in view
        """
        self.__lock.acquire()
        result = self.__satellites
        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def heading( self ):
        """! Retrieve true heading
        @return  heading (degrees)
        """
        self.__lock.acquire()
        result = self.__heading
        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def velocity( self ):
        """! Retrieve current velocity
        @return  velocity (km/hr)
        """
        self.__lock.acquire()
        result = self.__velocity
        self.__lock.release()

        return result

# =================================================================================================
class Grove_GPS( object ):
    """! Seeed Studio Grove-GPS Module (SIM28) """

    # ---------------------------------------------------------------------------------------------
    def __init__( self, port = '/dev/ttyAMA0', baud = 9600, timeout = 0 ):
        """! Initialize Class
        @param port  serial device
        @param baud  baud rate
        @param timeout  timeout
        """
        self.__ser = Grove_GPS_Serial( port, baud, timeout )
        self.__ser.start()
 
    # ---------------------------------------------------------------------------------------------
    def __del__( self ):
        """! Finalize Class """
        self.__ser.stop()

    # ---------------------------------------------------------------------------------------------
    def utc( self ):
        """! Retrieve UTC Time
        @return  utc time (hhmmss)
        """
        return self.__ser.utc()

    # ---------------------------------------------------------------------------------------------
    def date( self ):
        """! Retrieve UTC Date
        @return  date (ddmmyy)
        """
        return self.__ser.date()

    # ---------------------------------------------------------------------------------------------
    def location( self ):
        """! Retrieve current location
        @return  location as (latitude, longitude)
        """
        return self.__ser.location()

    # ---------------------------------------------------------------------------------------------
    def link( self ):
        """! Check for satellite link
        @return  @c True if link exists, @c False otherwise
        """
        return self.__ser.link()

    # ---------------------------------------------------------------------------------------------
    def altitude( self ):
        """! Retrieve current altitude
        @return  altitude (meters)
        """
        return self.__ser.altitude()

    # ---------------------------------------------------------------------------------------------
    def hdop( self ):
        """! Retrieve horizontal dilution of precision
        @return  hdop
        """
        return self.__ser.hdop()

    # ---------------------------------------------------------------------------------------------
    def satellitesInView( self ):
        """! Retrieve number of satellites in view
        @return  number of satellites in view
        """
        return self.__ser.satellitesInView()

    # ---------------------------------------------------------------------------------------------
    def heading( self ):
        """! Retrieve true heading
        @return  heading (degrees)
        """
        return self.__ser.heading()

    # ---------------------------------------------------------------------------------------------
    def velocity( self ):
        """! Retrieve current velocity
        @return  velocity (km/hr)
        """
        return self.__ser.velocity()

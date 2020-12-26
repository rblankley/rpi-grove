#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from serial_device import Serial_Device
from threading import Lock

import re
import time

__all__ = ['Grove_GPS']

# =================================================================================================
class Grove_GPS( object ):
    """! Seeed Studio Grove-GPS Module (SIM28) """

    DEBUG = False

    GPGGA = ["$GPGGA",
        "[0-9]{6}\.[0-9]{3}",                       # UTC Position (timestamp) hhmmss.sss
        "[0-9]+\.[0-9]{2,}",                        # Latitude of position ddmm.mmmmm
        "[NS]{1}",                                  # North or South Indicator
        "[0-9]+\.[0-9]{2,}",                        # Longitude of position ddmm.mmmmm
        "[EW]{1}",                                  # East or West Indicator
        "[0123]",                                   # GPS Position Indicator; 0=Fix not available or invalid, 1=GPS SPS Mode, fix valid, 2=Differential GPS, SPS Mode, fix valid, 3=GPS PPS Mode, fix valid 
        "[0-9]{1,2}",                               # Number of Satellites Used
        "[0-9]+\.[0-9]*",                           # Horizontal Dilution of Precision x.x
        "[0-9]+\.[0-9]*",                           # MSL Altitude x.x (meters)
        "\w",                                       # MSL Altitude units
        "-?[0-9]+\.[0-9]*",                         # Geoids Separation x.x (meters)
        "\w",                                       # Geoids Separation units
        ]

    GPGSA = ["$GPGSA",
        "[MA]{1}",                                  # Mode 1; M=Manual-forced to operate in 2D or 3D mode, A=Automatic-allowed to automatically switch 2D/3D
        "[123]{1}",                                 # Mode 2; 1=Fix not available, 2=3D, 3=3D
        "[0-9]*",                                   # Satellite Used on Channel 1
        "[0-9]*",                                   # Satellite Used on Channel 2
        "[0-9]*",                                   # Satellite Used on Channel 3
        "[0-9]*",                                   # Satellite Used on Channel 4
        "[0-9]*",                                   # Satellite Used on Channel 5
        "[0-9]*",                                   # Satellite Used on Channel 6
        "[0-9]*",                                   # Satellite Used on Channel 7
        "[0-9]*",                                   # Satellite Used on Channel 8
        "[0-9]*",                                   # Satellite Used on Channel 9
        "[0-9]*",                                   # Satellite Used on Channel 10
        "[0-9]*",                                   # Satellite Used on Channel 11
        "[0-9]*",                                   # Satellite Used on Channel 12
        "[0-9]+\.[0-9]*",                           # Position Dilution of Precision x.x
        "[0-9]+\.[0-9]*",                           # Horizontal Dilution of Precision x.x
        "[0-9]+\.[0-9]*",                           # Vertical Dilution of Precision x.x
        ]

    GPGSV = ["$GPGSV",
        "[1-9]{1}",                                 # Number of Messages
        "[1-9]{1}",                                 # Messages Number
        "[0-9]{1,2}",                               # Number of Satellites Used
        "[0-9]{1,2}",                               # Channel 1 Satellite ID (1-32)
        "[0-9]{1,2}",                               # Channel 1 Satellite Elevation (degrees, max 90)
        "[0-9]{1,3}",                               # Channel 1 Satellite Azinmuth (degrees true, 0-359)
        "[0-9]*",                                   # Channel 1 SNR(C/NO) dBHz (0-99, null when not tracking)
        ]

    GPRMC = ["$GPRMC",
        "[0-9]{6}\.[0-9]{3}",                       # UTS Position (timestamp) hhmmss.sss
        "[AV]{1}",                                  # Status; A=data valid, V=data not valid
        "[0-9]+\.[0-9]{2,}",                        # Latitude of position ddmm.mmmmm
        "[NS]{1}",                                  # North or South Indicator
        "[0-9]+\.[0-9]{2,}",                        # Longitude of position ddmm.mmmmm
        "[EW]{1}",                                  # East or West Indicator
        "[0-9]+\.[0-9]*",                           # Speed Over Ground (knots)
        "[0-9]+\.[0-9]*",                           # Course Over Ground Heading (degrees true)
        "[0-9]{6}",                                 # Date ddmmyy
        ]

    GPVTG = ["$GPVTG",
        "[0-9]+\.[0-9]*",                           # Measured Heading (degrees true)
        "[T]{1}",                                   # True
        "[0-9]+\.[0-9]*",                           # Measured Heading magnetic (degrees magnetic)
        "[M]{1}",                                   # Magnetic
        "[0-9]+\.[0-9]*",                           # Measured Horizontal Speed (knots)
        "[N]{1}",                                   # Knots
        "[0-9]+\.[0-9]*",                           # Measured Horizontal Speed (kilometers)
        "[K]{1}",                                   # Kilometers / hr
        ]

    KNOTS_TO_KM_HR = 1.852

    # ---------------------------------------------------------------------------------------------
    def __init__( self, port = '/dev/ttyAMA0', baud = 9600, timeout = 0 ):
        """! Initialize Class
        @param port  serial device
        @param baud  baud rate
        @param timeout  timeout
        """

        # GGA Global positioning system fixed data
        self.__gga = [] # contains compiled regex

        for p in self.GPGGA:
            self.__gga.append( re.compile( p ) ) # compile regex once to use later

        # GSA GNSS DOP and Active Satellites
        self.__gsa = [] # contains compiled regex

        for p in self.GPGSA:
            self.__gsa.append( re.compile( p ) ) # compile regex once to use later

        # GSV GNSS Satellites in View
        self.__gsv = [] # contains compiled regex

        for p in self.GPGSV:
            self.__gsv.append( re.compile( p ) ) # compile regex once to use later

        self.__gsv_lines = []

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
        self.__altitude = 0.0
        self.__geoids = 0.0

        self.__satellitesUsed = []
        self.__pdop = 0.0
        self.__hdop = 0.0
        self.__vdop = 0.0

        self.__satellitesUsedInfo = {}              # tuple of (elevation, azinmuth, SNR(C/NO)) by satellite id

        self.__heading = 0.0
        self.__velocity = 0.0

        self.__date = 0

        # start serial device
        self.__lock = Lock()

        self.__ser = Serial_Device( port, baud, timeout )
        self.__ser.on_process_command = self.__process_command
        self.__ser.start()

    # ---------------------------------------------------------------------------------------------
    def __del__( self ):
        """! Finalize Class """
        self.__ser.stop()

    # ---------------------------------------------------------------------------------------------
    def __debug( self, s ):
        """! Print debug statement
        @param s  statement
        """
        if ( self.DEBUG ):
            print( s )

    # ---------------------------------------------------------------------------------------------
    def __split( self, ident, line ):
        """! Split lines on separator
        @param ident  identifier
        @param line  line to split
        @return  array of lines
        """

        # sometimes multiple GPS data packets come into the stream... take the data only after the last ident is seen
        i = line.rindex( ident )
        line = line[i:]

        lines = line.split( "," )

        # look for checksum and strip
        checksum = lines[-1]

        if ( "*" in checksum ):
            i = checksum.index( "*" )
            lines[-1] = checksum[:i]

        return lines

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

        lines = self.__split( ident, line )
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
    def __process_gsv( self ):
        """! Process GSV line data """
        self.__satellitesUsedInfo = {}

        # process each line
        for line in self.__gsv_lines:
            lines = self.__split( self.GPGSV[0], line )

            # retrieve satellite info
            # message may contain up to 4 satellites
            for i in (4, 8, 12, 16):
                if ( i < len(lines) ):
                    sat_id = int( lines[i] )

                    if ( 0 < sat_id ):
                        values = []

                        # unused satellites may not contain elevation, azinmuth, snr
                        for j in range( 1, 4 ):
                            if ( len( lines[i+j] ) ):
                                values.append( int( lines[i+j] ) )
                            else:
                                values.append( None )

                        # (elevation, azinmuth, snr)
                        self.__satellitesUsedInfo[sat_id] = (values[0], values[1], values[2])

        self.__satellites = len( self.__satellitesUsedInfo )

    # ---------------------------------------------------------------------------------------------
    def __process_command( self, line ):
        """! Process command
        @param line  command to process
        """
        if ( not len( line ) ):
            return

        self.__lock.acquire()
        self.__debug( line )

        # gga
        if ( self.__validate_expression( self.GPGGA[0], line, self.__gga ) ):
            lines = self.__split( self.GPGGA[0], line )

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

        # gsa
        elif ( self.__validate_expression( self.GPGSA[0], line, self.__gsa ) ):
            lines = self.__split( self.GPGSA[0], line )

            if ( '1' == lines[2] ):
                self.__debug( "Fix not available" )

            else:
                self.__satellitesUsed = []

                for s in lines[3:15]:
                    if ( len(s ) ):
                        self.__satellitesUsed.append( int( s ) )

                self.__pdop = float( lines[15] )
                self.__hdop = float( lines[16] )
                self.__vdop = float( lines[17] )

        # gsv
        elif ( self.__validate_expression( self.GPGSV[0], line, self.__gsv ) ):
            lines = self.__split( self.GPGSV[0], line )

            num_gsv = int( lines[1] )
            gsv_index = int( lines[2] ) - 1

            # save off all lines
            # process them all once we have all of them
            if ( 0 == gsv_index ):
                self.__gsv_lines = []

            self.__gsv_lines.append( line )

            # we have all lines
            if ( num_gsv == len( self.__gsv_lines ) ):
                self.__process_gsv()

        # rmc
        elif ( self.__validate_expression( self.GPRMC[0], line, self.__rmc ) ):
            lines = self.__split( self.GPRMC[0], line )

            if ( 'A' != lines[2] ):
                self.__debug( "RMC data not valid" )

            else:
                self.__velocity = float( lines[7] ) * self.KNOTS_TO_KM_HR
                self.__heading = float( lines[8] )
                self.__date = float( lines[9] )

        # vtg
        elif ( self.__validate_expression( self.GPVTG[0], line, self.__vtg ) ):
            lines = self.__split( self.GPVTG[0], line )

            self.__heading = float( lines[1] )
            self.__velocity = float( lines[5] ) * self.KNOTS_TO_KM_HR

        self.__lock.release()

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
    def pdop( self ):
        """! Retrieve position dilution of precision
        @return  pdop
        """
        self.__lock.acquire()
        result = self.__pdop
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
    def vdop( self ):
        """! Retrieve vertical dilution of precision
        @return  hdop
        """
        self.__lock.acquire()
        result = self.__vdop
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
    def satellitesUsed( self ):
        """! Retrieve satellites used
        @return  satellites used
        """
        self.__lock.acquire()
        result = self.__satellitesUsed
        self.__lock.release()

        return result

    # ---------------------------------------------------------------------------------------------
    def satellitesUsedInfo( self ):
        """! Retrieve satellites used information
        @return  dictionary of (elevation, azinmuth, snr) by satellites used id
        """
        self.__lock.acquire()
        result = self.__satellitesUsedInfo
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
#
# Test Cases
#
# =================================================================================================

# -------------------------------------------------------------------------------------------------
def main():
    gps = Grove_GPS()

    try:

        while ( True ):

            # wait for link
            if ( not gps.link() ):
                print( "No link..." )

            else:
                print( 'Link' )
                print( 'UTC', gps.utc() )
                print( 'Date', gps.date() )
                
                (lat, lon) = gps.location()
                print( 'Latitude %.6f' % lat )
                print( 'Longitude %.6f' % lon )
                print( 'Altitude', gps.altitude() )

                print( 'PDOP', gps.pdop() )
                print( 'HDOP', gps.hdop() )
                print( 'VDOP', gps.vdop() )

                print( 'Satellites in view', gps.satellitesInView() )
                print( 'Satellites used', gps.satellitesUsed() )
                print( 'Satellites information', gps.satellitesUsedInfo() )

                print( 'Velocity', gps.velocity() )
                print( 'True Heading', gps.heading() )

            time.sleep( 1.0 )

    finally:
        del gps

# -------------------------------------------------------------------------------------------------
if __name__ =="__main__":
    main()
#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from datetime import datetime
from i2c_device import I2C_Device

# =================================================================================================
class Grove_RTC( object ):
    """! Seeed Studio Grove-RTC (DS1307 Real Time Clock) """

    # address
    I2C_ADDRESS = 0x68

    REG_SECONDS = 0x00
    REG_MINUTES = 0x01
    REG_HOURS = 0x02
    REG_DAY_OF_WEEK = 0x03
    REG_DATE = 0x04
    REG_MONTH = 0x05
    REG_YEAR = 0x06

    BIT_CLOCK_HALTED = 0x80

    BIT_AM_PM_ENABLED = 0x40
    BIT_PM = 0x20

    # ---------------------------------------------------------------------------------------------
    def __init__( self, enable = True ):
        """! Initialize Class
        @param enable  @c True to enable clock, @c false otherwise
        """

        # setup device
        self.__dev = I2C_Device( self.I2C_ADDRESS )

        # check disabled clock
        if ( enable ):
            self.setEnabled( True )

    # ---------------------------------------------------------------------------------------------
    def __decToBcd( self, val ):
        """! Convert Decimal value to BCD value
        @param val  value to convert
        @return  converted value
        """
        h = (val // 10) % 10
        l = val % 10

        return (h << 4) + l
 
    # ---------------------------------------------------------------------------------------------
    def __bcdToDec( self, val ):
        """! Convert BCD value to Decimal value
        @param val  value to convert
        @return  converted value
        """
        h = (val >> 4) & 0x0f
        l = val & 0x0f

        return (h * 10) + l

    # ---------------------------------------------------------------------------------------------
    def enabled( self ):
        """! Check if RTC oscillator enabled
        @return  @c True if enabled, @c False otherwise
        """
        reg = self.__dev.readReg( self.REG_SECONDS )

        if ( self.BIT_CLOCK_HALTED & reg ):
            return False

        return True

    # ---------------------------------------------------------------------------------------------
    def setEnabled( self, enabled ):
        """! Set RTC oscillator enabled
        @param enabled  @c True to enable, @c False otherwise
        """
        reg = self.__dev.readReg( self.REG_SECONDS )

        # start a halted clock
        if (( enabled ) and ( self.BIT_CLOCK_HALTED & reg )):
            reg &= ~(self.BIT_CLOCK_HALTED)

            self.__dev.writeReg( self.REG_SECONDS, reg )

        # stop a running clock
        elif (( not enabled ) and ( not (self.BIT_CLOCK_HALTED & reg) )):
            reg |= self.BIT_CLOCK_HALTED

            self.__dev.writeReg( self.REG_SECONDS, reg )

    # ---------------------------------------------------------------------------------------------
    def meridiemMode( self ):
        """! Check if RTC is in 12 or 24 hour mode
        @return  @c True when RTC in 12-hour mode, @c False otherwise
        """
        reg = self.__dev.readReg( self.REG_HOURS )

        if ( self.BIT_AM_PM_ENABLED & reg ):
            return True

        return False

    # ---------------------------------------------------------------------------------------------
    def setMeridiemMode( self, enabled ):
        """! Set if RTC is in 12 or 24 hour mode
        @param enabled  @c True to set RTC 12-hour mode, @c False otherwise
        """
        reg = self.__dev.readReg( self.REG_HOURS )

        # enable 12 hour clock
        if (( enabled ) and ( not (self.BIT_AM_PM_ENABLED & reg) )):
            reg |= self.BIT_AM_PM_ENABLED

            self.__dev.writeReg( self.REG_HOURS, reg )

        # disable 12 hour clock
        elif (( not enabled ) and ( self.BIT_AM_PM_ENABLED & reg )):
            reg &= ~(self.BIT_AM_PM_ENABLED)

            self.__dev.writeReg( self.REG_HOURS, reg )

    # ---------------------------------------------------------------------------------------------
    def time( self ):
        """! Retrieve Time
        @return  time (hhmmss)
        """
        data = self.__dev.readBlockData( self.REG_SECONDS, 3 )

        s = self.__bcdToDec( data[0] & 0x7f )
        m = self.__bcdToDec( data[1] & 0x7f )

        # 1-12 when 12 hour mode
        if ( self.BIT_AM_PM_ENABLED & data[2] ):
            h = self.__bcdToDec( data[2] & 0x1f )

            if ( self.BIT_PM & data[2] ):
                if ( 12 != h ):
                    h += 12
            elif ( 12 == h ):
                h = 0

        # 0-23 when 24 hour mode
        else:
            h = self.__bcdToDec( data[2] & 0x3f )

        return (10000 * h) + (100 * m) + s

    # ---------------------------------------------------------------------------------------------
    def setTime( self, value ):
        """! Set Time
        @param value  time (hhmmss)
        """
        h = (value // 10000) % 100
        m = (value // 100) % 100
        s = value % 100

        # read clock
        data = self.__dev.readBlockData( self.REG_SECONDS, 3 )

        data[0] &= self.BIT_CLOCK_HALTED
        data[0] |= self.__decToBcd( s )

        data[1] = self.__decToBcd( m )

        data[2] &= self.BIT_AM_PM_ENABLED

        if ( self.BIT_AM_PM_ENABLED & data[2] ):
            if ( 0 == h ):
                h = 12
            elif ( 12 == h ):
                data[2] |= self.BIT_PM
            elif ( 13 <= h ):
                data[2] |= self.BIT_PM
                h -= 12

        data[2] |= self.__decToBcd( h )

        self.__dev.writeBlockData( self.REG_SECONDS, data )

    # ---------------------------------------------------------------------------------------------
    def date( self ):
        """! Retrieve Date
        @return  date (ddmmyy)
        """
        data = self.__dev.readBlockData( self.REG_DATE, 3 )

        d = self.__bcdToDec( data[0] & 0x3f )
        m = self.__bcdToDec( data[1] & 0x1f )
        y = self.__bcdToDec( data[2] )

        return (10000 * d) + (100 * m) + y

    # ---------------------------------------------------------------------------------------------
    def setDate( self, value ):
        """! Set Date
        @param value  date (ddmmyy)
        """
        data = []
        data.append( self.__decToBcd( (value // 10000) % 100 ) )
        data.append( self.__decToBcd( (value // 100) % 100 ) )
        data.append( self.__decToBcd( value % 100 ) )

        self.__dev.writeBlockData( self.REG_DATE, data )

    # ---------------------------------------------------------------------------------------------
    def dayOfWeek( self ):
        """! Retrieve Day of Week
        @return  day; 1=Sun, 2=Mon, 3=Tue, etc...
        """
        return self.__dev.readReg( self.REG_DAY_OF_WEEK )

    # ---------------------------------------------------------------------------------------------
    def setDayOfWeek( self, value ):
        """! Set Day of Week
        @param value  day; 1=Sun, 2=Mon, 3=Tue, etc...
        """
        return self.__dev.writeReg( self.REG_DAY_OF_WEEK, value )

    # ---------------------------------------------------------------------------------------------
    def setDateTimeFromCurrent( self ):
        """! Set RTC date and time based on current """

        # current date and time
        now = datetime.now()

        d = now.strftime( "%d%m%y" )
        self.setDate( int( d ) )

        dow = now.weekday() # 0=Mon, 1=Tue, etc...
        dow += 2

        if ( 7 < dow ):
            dow -= 7

        self.setDayOfWeek( dow )

        t = now.strftime( "%H%M%S" )
        self.setTime( int( t ) )

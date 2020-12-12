#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

import sys

# =================================================================================================
class I2C_Device( object ):
    """! Abstract I2C Device """

    # ---------------------------------------------------------------------------------------------
    def __init__( self, i2c_address ):
        """! Initialize I2C Device
        @param i2c_address  i2c address
        """

        # retrieve bus
        if ( sys.platform == 'uwp' ):
            import winrt_smbus as smbus

            self.__bus = smbus.SMBus( 1 )
        else:
            import smbus
            import RPi.GPIO as GPIO

            rev = GPIO.RPI_REVISION
            if (( rev == 2 ) or ( rev == 3 )):
                self.__bus = smbus.SMBus( 1 )
            else:
                self.__bus = smbus.SMBus( 0 )

        self.__address = i2c_address

    # ---------------------------------------------------------------------------------------------
    def readReg( self, reg ):
        """! Read Register Data
        @param reg  register
        @return  data
        """
        if ( reg is None ):
            return self.__bus.read_byte( self.__address )

        return self.__bus.read_byte_data( self.__address, reg )

    # ---------------------------------------------------------------------------------------------
    def writeReg( self, reg, d ):
        """! Write Register Data
        @param reg  register
        @param d  data
        """
        if ( reg is None ):
            self.__bus.write_byte( self.__address, d )
            return

        self.__bus.write_byte_data( self.__address, reg, d )

    # ---------------------------------------------------------------------------------------------
    def readBlockData( self, reg, numbytes ):
        """! Read Block Data
        @param reg  register
        @param numbytes  number of bytes to read  
        """
        return self.__bus.read_i2c_block_data( self.__address, reg, numbytes )

    # ---------------------------------------------------------------------------------------------
    def writeBlockData( self, reg, d ):
        """! Read Block Data
        @param reg  register
        @param d  data
        """
        return self.__bus.write_i2c_block_data( self.__address, reg, d )

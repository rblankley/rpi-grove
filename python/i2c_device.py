#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

import sys

__all__ = ['I2C_Device']

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

            bus = 1

        else:
            import smbus

            try:
                import RPi.GPIO as GPIO
                # use the bus that matches your raspi version
                rev = GPIO.RPI_REVISION
            except:
                rev = 3

            if (( rev == 2 ) or ( rev == 3 )):
                bus = 1  # for Pi 2+
            else:
                bus = 0

        self.__bus = smbus.SMBus( bus )
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
    def readWordData( self, reg ):
        """! Read a single word (2-bytes)
        @param reg  register
        @return  data
        """
        return self.__bus.read_word_data( self.__address, reg )

    # ---------------------------------------------------------------------------------------------
    def writeWordData( self, reg, d ):
        """! Write a single word (2-bytes)
        @param reg  register
        @param d  data
        """
        self.__bus.write_word_data( self.__address, reg, d )

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

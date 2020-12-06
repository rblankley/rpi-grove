#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from enum import Enum
from i2c_device import I2C_Device

import time

# =================================================================================================
class DexterInd_Light_Color_Sensor_Gain( Enum ):
    """! Dexter Industries Light Color Sensor Gain Values """
    GAIN_1X, GAIN_4X, GAIN_16X, GAIN_60X = range( 0, 4 )

# =================================================================================================
class DexterInd_Light_Color_Sensor( object ):
    """! Dexter Industries Light Color Sensor (TCS34725) """

    # Constants
    I2C_ADDRESS = 0x29

    COMMAND_BIT = 0x80

    REG_ENABLE = 0x00
    REG_ATIME = 0x01                                # Integration time
    REG_WTIME = 0x03                                # Wait time (if ENABLE_WEN is asserted)
    REG_AILTL = 0x04                                # Clear channel lower interrupt threshold
    REG_AILTH = 0x05
    REG_AIHTL = 0x06                                # Clear channel upper interrupt threshold
    REG_AIHTH = 0x07
    REG_PERS = 0x0C                                 # Persistence register - basic SW filtering mechanism for interrupts
    REG_CONFIG = 0x0D
    REG_CONTROL = 0x0F                              # Set the gain level for the sensor
    REG_ID = 0x12                                   # 0x44 = TCS34721/TCS34725, 0x4D = TCS34723/TCS34727
    REG_STATUS = 0x13
    REG_CDATAL = 0x14                               # Clear channel data
    REG_CDATAH = 0x15
    REG_RDATAL = 0x16                               # Red channel data
    REG_RDATAH = 0x17
    REG_GDATAL = 0x18                               # Green channel data
    REG_GDATAH = 0x19
    REG_BDATAL = 0x1A                               # Blue channel data
    REG_BDATAH = 0x1B

    ENABLE_AIEN = 0x10                              # RGBC Interrupt Enable
    ENABLE_WEN = 0x08                               # Wait enable - Writing 1 activates the wait timer
    ENABLE_AEN = 0x02                               # RGBC Enable - Writing 1 actives the ADC, 0 disables it
    ENABLE_PON = 0x01                               # Power on - Writing 1 activates the internal oscillator, 0 disables it

    PERS_NONE = 0b0000                              # Every RGBC cycle generates an interrupt
    PERS_1_CYCLE = 0b0001                           # 1 clean channel value outside threshold range generates an interrupt
    PERS_2_CYCLE = 0b0010                           # 2 clean channel values outside threshold range generates an interrupt
    PERS_3_CYCLE = 0b0011                           # 3 clean channel values outside threshold range generates an interrupt
    PERS_5_CYCLE = 0b0100                           # 5 clean channel values outside threshold range generates an interrupt
    PERS_10_CYCLE = 0b0101                          # 10 clean channel values outside threshold range generates an interrupt
    PERS_15_CYCLE = 0b0110                          # 15 clean channel values outside threshold range generates an interrupt
    PERS_20_CYCLE = 0b0111                          # 20 clean channel values outside threshold range generates an interrupt
    PERS_25_CYCLE = 0b1000                          # 25 clean channel values outside threshold range generates an interrupt
    PERS_30_CYCLE = 0b1001                          # 30 clean channel values outside threshold range generates an interrupt
    PERS_35_CYCLE = 0b1010                          # 35 clean channel values outside threshold range generates an interrupt
    PERS_40_CYCLE = 0b1011                          # 40 clean channel values outside threshold range generates an interrupt
    PERS_45_CYCLE = 0b1100                          # 45 clean channel values outside threshold range generates an interrupt
    PERS_50_CYCLE = 0b1101                          # 50 clean channel values outside threshold range generates an interrupt
    PERS_55_CYCLE = 0b1110                          # 55 clean channel values outside threshold range generates an interrupt
    PERS_60_CYCLE = 0b1111                          # 60 clean channel values outside threshold range generates an interrupt

    CONFIG_WLONG = 0x02                             # Choose between short and long (12x) wait times via WTIME

    STATUS_AINT = 0x10                              # RGBC Clean channel interrupt
    STATUS_AVALID = 0x01                            # Indicates that the RGBC channels have completed an integration cycle

    SENSOR_GAIN = {
        DexterInd_Light_Color_Sensor_Gain.GAIN_1X: [0x00, 1],
        DexterInd_Light_Color_Sensor_Gain.GAIN_4X: [0x01, 4],
        DexterInd_Light_Color_Sensor_Gain.GAIN_16X: [0x02, 16],
        DexterInd_Light_Color_Sensor_Gain.GAIN_60X: [0x03, 60],
    }

    # ---------------------------------------------------------------------------------------------
    def __init__( self, integration_time = 0.0024, gain = DexterInd_Light_Color_Sensor_Gain.GAIN_16X ):
        """! Initialize the sensor
        Keyword arguments:
        @param integration_time  time in seconds for each sample; use 0.0024 second (2.4ms) increments (range of 0.0024...0.6144 seconds)
        @param gain  gain constant
        """

        # setup device
        self.__dev = I2C_Device( self.I2C_ADDRESS )

        # make sure we are connected to the right sensor
        chip_id = self.__readReg( self.REG_ID )
        if ( chip_id != 0x44 ):
            self.__valid = False

        else:
            self.__valid = True

            # set default integration time and gain
            self.setIntegrationTime( integration_time )
            self.setGain( gain )

            # enable the device (by default, the device is in power down mode on bootup).
            self.setEnabled( True )

    # ---------------------------------------------------------------------------------------------
    def __readReg( self, addr ):
        """! Read Register Data
        @param addr  address
        @return  data
        """
        return self.__dev.readReg( (self.COMMAND_BIT | addr) )

    # ---------------------------------------------------------------------------------------------
    def __writeReg( self, addr, d ):
        """! Write Register Data
        @param addr  address
        @param d  data
        """
        self.__dev.writeReg( (self.COMMAND_BIT | addr), d )

    # ---------------------------------------------------------------------------------------------
    def __readBlockData( self, addr, numbytes ):
        """! Read Block Data
        @param addr  address
        @param numbytes  number of bytes to read  
        """
        return self.__dev.readBlockData( (self.COMMAND_BIT | addr), numbytes )

    # ---------------------------------------------------------------------------------------------
    def setEnabled( self, enabled ):
        """! Enable the sensor
        @param enabled  @c True to enable, @c False otherwise
        """
        if ( not self.__valid ):
            return

        elif ( enabled ):
            # Set the power and enable bits.
            self.__writeReg( self.REG_ENABLE, self.ENABLE_PON )
            time.sleep( 0.01 )

            self.__writeReg( self.REG_ENABLE, (self.ENABLE_PON | self.ENABLE_AEN) )

        else:
            # Clear the power and enable bits.
            reg = self.__readReg( self.REG_ENABLE )
            reg &= ~(self.ENABLE_PON | self.ENABLE_AEN)

            self.__writeReg( self.REG_ENABLE, reg )

    # ---------------------------------------------------------------------------------------------
    def setIntegrationTime( self, time ):
        """! Set the integration (sampling) time for the sensor
        @param time  Time in seconds for each sample; use 0.0024 second (2.4ms) increments (clipped to the range of 0.0024...0.6144 seconds)
        """
        if ( not self.__valid ):
            return

        val = int( 0x100 - (time / 0.0024) )
        if val > 255:
            val = 255
        elif val < 0:
            val = 0

        self.__writeReg( self.REG_ATIME, val )
        self.__integration_time_val = 256 - val

    # ---------------------------------------------------------------------------------------------
    def setGain( self, gain ):
        """! Set the sensor gain (light sensitivity)
        @param gain  gain constant
        """
        if ( not self.__valid ):
            return

        reg, self.__gain = self.SENSOR_GAIN[gain]

        self.__writeReg( self.REG_CONTROL, reg )

    # ---------------------------------------------------------------------------------------------
    def setLightEnabled( self, enabled, delay=True ):
        """! Set LED Light enabled
        @param enabled  @c True to enable, @c False otherwise
        @param delay  delay for the time it takes to sample; this ensures next reading will have LED light enabled
        """
        if ( not self.__valid ):
            return

        self.__writeReg( self.REG_PERS, self.PERS_NONE )

        reg = self.__readReg( self.REG_ENABLE )
        if ( enabled ):
            reg |= self.ENABLE_AIEN
        else:
            reg &= ~self.ENABLE_AIEN

        self.__writeReg( self.REG_ENABLE, reg )

        if ( delay ):
            # delay for twice the integration time to ensure the LED state change has taken effect and a full sample has been made before the next reading
            time.sleep( 2 * (self.__integration_time_val * 0.0024) ) 

    # ---------------------------------------------------------------------------------------------
    def values( self, delay=True ):
        """! Read the Red Green Blue and Clear values from the sensor
        @param delay  delay for the time it takes to sample; this allows immediately consecutive readings that are not redundant
        @return  raw values as a 4-tuple on a scale of 0-1 (red, green, blue, clear)
        """
        if ( not self.__valid ):
            return

        if ( delay ):
            # delay for the integration time to allow reading immediately after the previous read
            time.sleep( self.__integration_time_val * 0.0024 )

        div = 1024.0 * self.__integration_time_val

        # read each color register
        data = self.__readBlockData( self.REG_CDATAL, 8 )

        if ( 8 != len(data) ):
            return None

        c = float((data[1] << 8) | data[0]) / div
        r = float((data[3] << 8) | data[2]) / div
        g = float((data[5] << 8) | data[4]) / div
        b = float((data[7] << 8) | data[6]) / div

        if ( c > 1 ):
            c = 1
        if ( r > 1 ):
            r = 1
        if ( g > 1 ):
            g = 1
        if ( b > 1 ):
            b = 1

        return ( r, g, b, c )

    # ---------------------------------------------------------------------------------------------
    def rgb( self, delay=True ):
        """! Read the 8-bit RGB values from the sensor
        @param delay  delay for the time it takes to sample; this allows immediately consecutive readings that are not redundant
        @return  raw values as a 3-tuple on a scale of 0-255 (red, green, blue)
        """
        colors = self.values( delay )
        if ( colors is None ):
            return ( 0, 0, 0 )
        elif ( 0 == colors[3] ):
            return ( 0, 0, 0 )

        r = int( pow( colors[0] / colors[3], 2.5 ) * 255 )
        g = int( pow( colors[1] / colors[3], 2.5 ) * 255 )
        b = int( pow( colors[2] / colors[3], 2.5 ) * 255 )

        # handle possible 8-bit overflow
        if ( r > 255 ):
            r = 255
        if ( g > 255 ):
            g = 255
        if ( b > 255 ):
            b = 255

        return ( r, g, b )

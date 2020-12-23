#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from enum import Enum
from i2c_device import I2C_Device

from grove_ports import Grove_Analog_Port
from grove_ports import Grove_Digital_Port

__all__ = ['Grove_Base_Hat_Device_Type', 'Grove_Base_Hat_Analog_Read_Type', 'Grove_Base_Hat_Device']

# =================================================================================================
class Grove_Base_Hat_Device_Type( Enum ):
    """! Grove Base Hat Types """
    RPI_HAT, RPI_ZERO_HAT = range( 0, 2 )

# =================================================================================================
class Grove_Base_Hat_Analog_Read_Type( Enum ):
    """! Grove Base Hat Analog Read Types """
    RAW, VOLTAGE, VALUE = range( 0, 3 )

# =================================================================================================
class Grove_Base_Hat_Device( object ):
    """! Seeed Studio Grove Base Hat """

    # address
    I2C_ADDRESS = 0x04

    REG_TYPE = 0x00
    REG_VERSION = 0x02

    REG_POWER_SUPPLY_VOLTAGE = 0x29

    REG_RAW_BASE = 0x10
    REG_VOLTAGE_BASE = 0x20
    REG_VALUE_BASE = 0x30

    RPI_HAT_PIDS = {
        4: (Grove_Base_Hat_Device_Type.RPI_HAT, 'Grove Base Hat RPi'),
        5: (Grove_Base_Hat_Device_Type.RPI_ZERO_HAT, 'Grove Base Hat RPi Zero'),
    }

    ANALOG_PORTS = {}
    DIGITAL_PORTS = {}

    ANALOG_READ_BASE = {
        Grove_Base_Hat_Analog_Read_Type.RAW: REG_RAW_BASE,
        Grove_Base_Hat_Analog_Read_Type.VOLTAGE: REG_VOLTAGE_BASE,
        Grove_Base_Hat_Analog_Read_Type.VALUE: REG_VALUE_BASE,
    }

    # ---------------------------------------------------------------------------------------------
    def __init__( self ):
        """! Initialize Class """

        # setup device
        self.__dev = I2C_Device( self.I2C_ADDRESS )

        # setup ports
        (dt, desc) = self.deviceType

        if ( Grove_Base_Hat_Device_Type.RPI_ZERO_HAT == dt ):
            self.ANALOG_PORTS[Grove_Analog_Port.A0] = 0
            self.ANALOG_PORTS[Grove_Analog_Port.A2] = 2
            self.ANALOG_PORTS[Grove_Analog_Port.A4] = 4

            self.DIGITAL_PORTS[Grove_Digital_Port.D5] = 5
            self.DIGITAL_PORTS[Grove_Digital_Port.D16] = 16

        elif ( Grove_Base_Hat_Device_Type.RPI_HAT == dt ):
            self.ANALOG_PORTS[Grove_Analog_Port.A0] = 0
            self.ANALOG_PORTS[Grove_Analog_Port.A2] = 2
            self.ANALOG_PORTS[Grove_Analog_Port.A4] = 4
            self.ANALOG_PORTS[Grove_Analog_Port.A6] = 6

            self.DIGITAL_PORTS[Grove_Digital_Port.D5] = 5
            self.DIGITAL_PORTS[Grove_Digital_Port.D16] = 16
            self.DIGITAL_PORTS[Grove_Digital_Port.D18] = 18
            self.DIGITAL_PORTS[Grove_Digital_Port.D22] = 22
            self.DIGITAL_PORTS[Grove_Digital_Port.D24] = 24
            self.DIGITAL_PORTS[Grove_Digital_Port.D26] = 26

    # ---------------------------------------------------------------------------------------------
    def __read_register( self, reg ):
        """! Read 16 bit register
        Read the ADC Core (through I2C) registers
        Grove Base Hat for RPI I2C Registers
            - 0x00 ~ 0x01: 
            - 0x10 ~ 0x17: ADC raw data
            - 0x20 ~ 0x27: input voltage
            - 0x29: output voltage (Grove power supply voltage)
            - 0x30 ~ 0x37: input voltage / output voltage
        @param reg  register address
        @return  16-bit register value
        """
        return self.__dev.readWordData( reg )

    # ---------------------------------------------------------------------------------------------
    @property
    def deviceType( self ):
        """! Retrieve device type
        @return  device type as (type, text description)
        """
        id = self.__read_register( self.REG_TYPE )
        return self.RPI_HAT_PIDS[id]

    # ---------------------------------------------------------------------------------------------
    @property
    def powerSupplyVoltage( self ):
        """! Retrieve power supply voltage
        @return  voltage (in v)
        """
        val = float( self.__read_register( self.REG_POWER_SUPPLY_VOLTAGE ) ) / 1000.0
        return val

    # ---------------------------------------------------------------------------------------------
    @property
    def version( self ):
        """! Retrieve version
        @return  version
        """
        return self.__read_register( self.REG_VERSION )

    # ---------------------------------------------------------------------------------------------
    def analogRead( self, port, rt=Grove_Base_Hat_Analog_Read_Type.VALUE ):
        """! Perform analog read
        @param port  port to read
        @param rt  read type to perform, where
                   @c Grove_Base_Hat_Analog_Read_Type.RAW is read raw adc value [0-4095]
                   @c Grove_Base_Hat_Analog_Read_Type.VOLTAGE is read voltage value in mV
                   @c Grove_Base_Hat_Analog_Read_Type.VALUE is read voltage ratio as percentage in 0.1%
        @return  value
        """
        return self.__read_register( self.ANALOG_READ_BASE[rt] + self.ANALOG_PORTS[port] )

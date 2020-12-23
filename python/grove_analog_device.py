#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

__all__ = ['Grove_Analog_Device']

# =================================================================================================
class Grove_Analog_Device( object ):
    """! Abstract Grove Analog Device """

    # ---------------------------------------------------------------------------------------------
    def __init__( self, dev, port ):
        """! Initialize I2C Device
        @param dev  grove device
        @param port  grove analog port
        """
        self.__dev = dev
        self.__port = port

    # ---------------------------------------------------------------------------------------------
    def read( self ):
        """! Read Device
        @return  value
        """
        return self.__dev.analogRead( self.__port )

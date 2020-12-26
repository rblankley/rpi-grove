#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

__all__ = ['Grove_Digital_Device']

# =================================================================================================
class Grove_Digital_Device( object ):
    """! Abstract Grove Digital Device """

    # ---------------------------------------------------------------------------------------------
    def __init__( self, dev, port, direction ):
        """! Initialize Device
        @param dev  grove device
        @param port  grove digital port
        @param direction  grove digital port direction
        """
        self.__gpio = dev.gpio( port, direction )

    # ---------------------------------------------------------------------------------------------
    def read( self ):
        """! Read Device
        @return  value
        """
        return self.__gpio.read()

    # ---------------------------------------------------------------------------------------------
    def write( self, value ):
        """! Write Device
        @param value  value to write
        """
        return self.__gpio.write( value )

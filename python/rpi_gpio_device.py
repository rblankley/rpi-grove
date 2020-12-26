#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from grove_ports import Grove_Digital_Port_Direction

import RPi.GPIO

__all__ = ['GPIO_Device']

RPi.GPIO.setwarnings( False )
RPi.GPIO.setmode( RPi.GPIO.BCM )

# =================================================================================================
class GPIO_Device( object ):
    """! Abstract GPIO Device for Raspberry Pi """

    PIN_DIRS = {
        Grove_Digital_Port_Direction.INPUT: RPi.GPIO.IN,
        Grove_Digital_Port_Direction.OUTPUT: RPi.GPIO.OUT,
    }

    # ---------------------------------------------------------------------------------------------
    def __init__( self, pin, direction=None ):
        """! Initialize Device
        @param pin  gpio pin number (BCM)
        @param direction  port direction
        """
        self.pin = pin
        self.direction = None

        if ( direction is not None ):
            self.pinMode( direction )

        self.__event_handle = None

    # ---------------------------------------------------------------------------------------------
    def __on_event( self, pin ):
        """! Pin Event Handler
        @param pin  gpio pin number (BCM)
        """
        value = self.read()
        if ( self.__event_handle ):
            self.__event_handle( pin, value )

    # ---------------------------------------------------------------------------------------------
    def pinMode( self, direction ):
        """! Set pin direction
        @param direction  port direction
        """
        self.direction = direction

        RPi.GPIO.setup( self.pin, self.PIN_DIRS[self.direction] )

    # ---------------------------------------------------------------------------------------------
    def read( self ):
        """! Read pin
        @return  pin value
        """
        return RPi.GPIO.input( self.pin )

    # ---------------------------------------------------------------------------------------------
    def write( self, value ):
        """! Write pin
        @param value  pin value
        """
        RPi.GPIO.output( self.pin, value )

    # ---------------------------------------------------------------------------------------------
    @property
    def on_event( self ):
        """! Retrieve event handler
        @return  event handle
        """
        return self.__event_handle

    # ---------------------------------------------------------------------------------------------
    @on_event.setter
    def on_event( self, handle ):
        """! Set event handler
        @param handle  event handle
        """
        if ( not callable( handle ) ):
            return

        if ( self.__event_handle is None ):
            RPi.GPIO.add_event_detect( self.pin, RPi.GPIO.BOTH, self.__on_event )

        self.__event_handle = handle

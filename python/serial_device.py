#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from threading import Lock, Thread

import serial
import time

__all__ = ['Serial_Device']

# =================================================================================================
class Serial_Device( Thread ):
    """! Thread object that manages serial communication """

    POLL_TIME = 0.05

    # ---------------------------------------------------------------------------------------------
    def __init__( self, port, baud, timeout=0 ):
        """! Initialize Class
        @param port  serial device
        @param baud  baud rate
        @param timeout  timeout
        """
        super( Serial_Device, self ).__init__()
        
        # daemonize thread
        self.daemon = True

        self.__ser = serial.Serial( port, baud, timeout=timeout )
        self.__ser.flush()

        self.__lock = Lock()

        self.__quit = False

        self.__process_command_handle = None

    # ---------------------------------------------------------------------------------------------
    def stop( self ):
        """! Stop thread and wait for completion """
        self.__lock.acquire()
        self.__quit = True
        self.__lock.release()

        self.join()

    # ---------------------------------------------------------------------------------------------
    @property
    def on_process_command( self ):
        """! Retrieve callback handle for process command
        @return  handle
        """
        self.__lock.acquire()
        handle = self.__process_command_handle
        self.__lock.release()

        return handle

    # ---------------------------------------------------------------------------------------------
    @on_process_command.setter
    def on_process_command( self, handle ):
        """! Set callback handle for process command
        @param handle  callback handle
        """
        if not callable( handle ):
            return

        self.__lock.acquire()
        self.__process_command_handle = handle
        self.__lock.release()

    # ---------------------------------------------------------------------------------------------
    def run( self ):
        """! Thread run method """
        buffer = []

        while ( True ):
            self.__lock.acquire()

            handle = self.__process_command_handle
            commands = []

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

                            if ( len( line ) ):
                                commands.append( line )

                            buffer = []

            finally:
                self.__lock.release()

            # process all commands
            if ( callable( handle ) ):
                for command in commands:
                    handle( command )

            # sleep until next polling time
            time.sleep( self.POLL_TIME )

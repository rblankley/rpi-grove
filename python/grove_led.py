#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from grove_digital_device import Grove_Digital_Device
from grove_ports import Grove_Digital_Port_Direction

import time

__all__ = ['Grove_LED']

# =================================================================================================
class Grove_LED( Grove_Digital_Device ):
    """! Grove LED (Digital) """

    # ---------------------------------------------------------------------------------------------
    def __init__( self, dev, port ):
        """! Initialize Device
        @param dev  grove device
        @param port  grove analog port
        """
        super( Grove_LED, self ).__init__( dev, port, Grove_Digital_Port_Direction.OUTPUT )

    # ---------------------------------------------------------------------------------------------
    def on( self ):
        """ Turn LED On """
        self.write( True )

    # ---------------------------------------------------------------------------------------------
    def off( self ):
        """ Turn LED Off """
        self.write( False )

# =================================================================================================
#
# Test Cases
#
# =================================================================================================

# -------------------------------------------------------------------------------------------------
def main():
    from grove_base_hat_device import Grove_Base_Hat_Device
    from grove_ports import Grove_Digital_Port

    import time

    # assume port D16 on a Grove Base Hat
    dev = Grove_Base_Hat_Device()
    port = Grove_Digital_Port.D16

    led = Grove_LED( dev, port )

    while True:
        led.on()
        time.sleep( 1 )
        led.off()
        time.sleep( 1 )

# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()

#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from grove_analog_device import Grove_Analog_Device

__all__ = ['Grove_Rotary_Angle_Sensor']

# =================================================================================================
class Grove_Rotary_Angle_Sensor( Grove_Analog_Device ):
    """! Grove Rotary Angle Sensor (Analog) """

    # ---------------------------------------------------------------------------------------------
    def __init__( self, dev, port ):
        """! Initialize Device
        @param dev  grove device
        @param port  grove analog port
        """
        super( Grove_Rotary_Angle_Sensor, self ).__init__( dev, port )

# =================================================================================================
def main():
    from grove_base_hat_device import Grove_Base_Hat_Device
    from grove_ports import Grove_Analog_Port

    import time

    # assume port A0 on a Grove Base Hat
    dev = Grove_Base_Hat_Device()
    port = Grove_Analog_Port.A0

    sensor = Grove_Rotary_Angle_Sensor( dev, port )

    while True:
        print( 'Rotary Value: {}'.format( sensor.read() ) )
        time.sleep( 0.2 )

# =================================================================================================
if __name__ == '__main__':
    main()

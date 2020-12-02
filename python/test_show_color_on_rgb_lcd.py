#!/usr/bin/env python

from di_light_color_sensor import DexterInd_Light_Color_Sensor, DexterInd_Light_Color_Sensor_Gain
from grove_rgb_lcd import Grove_RGB_LCD

# -------------------------------------------------------------------------------------------------
def main():
    s = DexterInd_Light_Color_Sensor()
    s.setLightEnabled( True )

    s.setGain( DexterInd_Light_Color_Sensor_Gain.GAIN_16X )
    s.setIntegrationTime( 42 * .0024 )

    disp = Grove_RGB_LCD()

    for i in range( 0, 600 ):
        (r, g, b) = s.rgb()

        disp.clear()
        disp.printText( '{0} {1} {2}'.format( r, g, b ) )
        disp.setColor( r, g, b )

    s.setLightEnabled( False )
    s.setEnabled( False )
    
    disp.clear()

# -------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

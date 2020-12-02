#!/usr/bin/env python

from di_light_color_sensor import DexterInd_Light_Color_Sensor, DexterInd_Light_Color_Sensor_Gain

import time

# -------------------------------------------------------------------------------------------------
def readLoop( s ):
    for i in range( 0, 10 ):
        print( s.rgb() )
        time.sleep( 2 )

# -------------------------------------------------------------------------------------------------
def main():
    s = DexterInd_Light_Color_Sensor()

    readLoop( s )

    s.setLightEnabled( True )
    readLoop( s )

    s.setIntegrationTime( 4 * 0.0024 )
    readLoop( s )

    s.setGain( DexterInd_Light_Color_Sensor_Gain.GAIN_60X )
    readLoop( s )

    s.setLightEnabled( False )
    readLoop( s )

    s.setEnabled( False )
    readLoop( s )

# -------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

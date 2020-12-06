#!/usr/bin/env python

from grove_gps_module import Grove_GPS

import time

# -------------------------------------------------------------------------------------------------
if __name__ =="__main__":
    gps = Grove_GPS()

    for _ in range( 0, 30 ):
        # wait for link
        if ( not gps.link() ):
            print( "No link..." )

        else:
            print( 'Link' )
            print( 'UTC', gps.utc() )
            print( 'Date', gps.date() )
            
            (lat, lon) = gps.location()
            print( 'Latitude %.6f' % lat )
            print( 'Longitude %.6f' % lon )
            
            print( 'Altitude', gps.altitude() )
            print( 'HDOP', gps.hdop() )
            print( 'Satellites in view', gps.satellitesInView() )

            print( 'Velocity', gps.velocity() )
            print( 'True Heading', gps.heading() )

        time.sleep( 1.0 )
    
    del gps

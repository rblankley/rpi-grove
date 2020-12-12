#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from grove_rgb_lcd import Grove_RGB_LCD

import socket 
import time

HOST_ADDR = "8.8.8.8"

# -------------------------------------------------------------------------------------------------
def gethostinfo():
    try:
        host_name = socket.gethostname()

        # ip address of internet facing adapter
        s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        s.connect( (HOST_ADDR, 80) )
        host_ip = s.getsockname()[0]

        return (host_name, host_ip)

    except KeyboardInterrupt:
        raise KeyboardInterrupt

    except:
        print( "Unable to get Hostname and IP" )

    return (None, None)

# -------------------------------------------------------------------------------------------------
def main():
    hostname = None
    ipaddr = None

    refresh = True

    d = Grove_RGB_LCD()

    while True:
        # retrieve host information
        (host_name, host_ip) = gethostinfo()

        # check for changes, refresh display if changes
        if (( hostname != host_name ) or ( ipaddr != host_ip )):
            hostname = host_name
            ipaddr = host_ip

            refresh = True

        # refresh display
        if ( refresh ):
            print("refresh")
            d.clear()

            if (( hostname is None ) or ( ipaddr is None )):
                d.setColor( 255, 0, 0 )
                d.printText( "No Host Info" )
            else:
                d.setColor( 0, 255, 0 )
                d.printText( hostname + "\n" + ipaddr, True )

            refresh = False

        time.sleep( 0.5 )

# -------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

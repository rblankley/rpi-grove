#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from grove_rtc import Grove_RTC

import time

# -------------------------------------------------------------------------------------------------
def testClock( rtc ):
    
    rtc.setDate( 10203 )
    rtc.setDayOfWeek( 7 )
    rtc.setTime( 5950 )

    time.sleep( 5.75 )

    if ( 5955 != rtc.time() ):
        print( "Fail Time 1", rtc.time() )

    rtc.setEnabled( False )

    if ( rtc.enabled() ):
        print( "Fail Disable" )

    time.sleep( 5 )

    if ( 5955 != rtc.time() ):
        print( "Fail Time 2", rtc.time() )

    rtc.setEnabled( True )

    if ( not rtc.enabled() ):
        print( "Fail Enable" )

    time.sleep( 5.75 )

    if ( 10000 != rtc.time() ):
        print( "Fail Time 3", rtc.time() )

    # ---- #

    rtc.setTime( 115955 )

    time.sleep( 5.75 )

    if ( 120000 != rtc.time() ):
        print( "Fail Rollover 1", rtc.time() )

    # ---- #

    rtc.setTime( 235955 )

    time.sleep( 5.75 )

    if ( 0 != rtc.time() ):
        print( "Fail Rollover 2", rtc.time() )

    if ( 20203 != rtc.date() ):
        print( "Fail Rollover 2 Date", rtc.date() )

    if ( 1 != rtc.dayOfWeek() ):
        print( "Fail Rollover 2 DOW", rtc.dayOfWeek() )

# -------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    rtc = Grove_RTC()

    print( "Current Date", rtc.date() )
    print( "Current Week Day", rtc.dayOfWeek() )
    print( "Current Time", rtc.time() )

    rtc.setMeridiemMode( True )

    if ( not rtc.meridiemMode() ):
        print( "Fail" )

    print( "Test Meridiem Mode (12 hour clock)" )
    testClock( rtc )
    
    rtc.setMeridiemMode( False )

    if ( rtc.meridiemMode() ):
        print( "Fail" )

    print( "Test Non-Meridiem Mode (24 hour clock)" )
    testClock( rtc )

    print( "Setting date to now" )
    rtc.setDateTimeFromCurrent()
    
    print( "Current Date", rtc.date() )
    print( "Current Week Day", rtc.dayOfWeek() )
    print( "Current Time", rtc.time() )

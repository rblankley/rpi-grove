#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

import time

from grove_rgb_lcd import Grove_RGB_LCD

# -------------------------------------------------------------------------------------------------
def scrollBackAndForth( d ):

    for i in range( 0, 3 ):
        d.scrollDisplayLeft()
        time.sleep( 0.5 )

    for i in range( 0, 6 ):
        d.scrollDisplayRight()
        time.sleep( 0.5 )

    for i in range( 0, 3 ):
        d.scrollDisplayLeft()
        time.sleep( 0.5 )

# -------------------------------------------------------------------------------------------------
def turnDisplayOnAndOff( d ):
    d.setDisplayEnabled( False )
    time.sleep( 0.5 )

    d.setDisplayEnabled( True )
    time.sleep( 0.5 )

    d.setDisplayEnabled( False )
    time.sleep( 0.5 )

    d.setDisplayEnabled( True )
    time.sleep( 0.5 )

    d.setDisplayEnabled( False )
    time.sleep( 0.5 )

    d.setDisplayEnabled( True )
    time.sleep( 0.5 )

# -------------------------------------------------------------------------------------------------
def moveCursorAround( d ):
    d.setCursorPos( 15, 1 )
    time.sleep( 1 )

    d.setCursorPos( 7, 1 )
    time.sleep( 1 )

    d.setCursorPos( 0, 1 )
    time.sleep( 1 )

    d.setCursorPos( 15, 0 )
    time.sleep( 1 )

    d.setCursorPos( 7, 0 )
    time.sleep( 1 )

    d.setCursorPos( 0, 0 )
    time.sleep( 1 )

# -------------------------------------------------------------------------------------------------
def colorRange( upward ):
    if ( upward ):
        return range( 64, 192, 16 )

    return range( 192, 64, -16 )

# -------------------------------------------------------------------------------------------------
def main():
    d = Grove_RGB_LCD()

    d.clear()
    d.printText( "Display On+Off" )
    turnDisplayOnAndOff( d )

    # ---- #

    d.clear()
    d.setAutoScroll( True )
    d.printText( "----------------Auto Scroll YES ********" )

    for i in range( 0, 16 ):
        d.printText( "X" )
        time.sleep( 0.25 )

    time.sleep( 2 )

    d.setAutoScroll( False )

    d.clear()
    d.printText( "----------------Auto Scroll NO  ********" )

    for i in range( 0, 16 ):
        d.printText( "X" )
        time.sleep( 0.25 )

    time.sleep( 2 )

    # ---- #

    d.clear()
    d.setLeftToRight( False )
    d.setCursorPos( 15, 0 )

    d.printText( "11111111" )
    time.sleep( 1 )
    d.printText( "22222222" )
    time.sleep( 1 )
    d.printText( "33333333" )
    time.sleep( 1 )
    d.printText( "44444444" )
    time.sleep( 1 )
    d.printText( "55555555" )
    time.sleep( 1 )
    d.printText( "66666666" )
    time.sleep( 1 )
    d.printText( "77777777" )
    time.sleep( 1 )
    d.printText( "88888888" )
    time.sleep( 1 )

    d.setLeftToRight( True )

    # ---- #

    d.clear()
    d.printText( "Word\nWrapping", True )
    time.sleep( 2 )

    d.printText( "Wrapping        Words Around", True )
    time.sleep( 2 )

    # ---- #

    d.clear()
    d.printText( "NoCursor" )
    time.sleep( 2 )

    d.clear()
    d.setCursor( True )
    d.printText( "Cursor" )
    time.sleep( 2 )

    d.clear()
    d.setCursor( True )
    d.setCursorBlink( True )
    d.printText( "Cursor+Blink" )
    time.sleep( 2 )

    d.clear()
    d.setCursor( False )
    d.printText( "BlinkOnly" )
    time.sleep( 2 )

    d.clear()
    d.setCursorBlink( False )
    d.setBlink( True )
    d.printText( "RGB Blink" )
    time.sleep( 4 )

    d.setBlink( False )

    # ---- #

    d.home()
    d.setCursorBlink( True )

    d.printText( "MovingCursor" )
    moveCursorAround( d )

    d.setCursorBlink( False )

    # ---- #

    # smile face
    charmap = []
    charmap.append( 0x1b )
    charmap.append( 0x1b )
    charmap.append( 0x00 )
    charmap.append( 0x04 )
    charmap.append( 0x00 )
    charmap.append( 0x11 )
    charmap.append( 0x0e )
    charmap.append( 0x00 ) # 8th line is cursor position

    d.createChar( 0, charmap )

    d.home()
    d.printText( "\x00" )

    time.sleep( 3 )

    # ---- #

    d.home()
    d.printText( "Scrolling Left+Right on screen" )
    scrollBackAndForth( d )

    # ---- #

    d.clear()
    d.printText( "Colors" )

    upwardg = True
    upwardb = True

    for r in colorRange( True ):
        for g in colorRange( upwardg ):
            for b in colorRange( upwardb ):
                d.setColor( r, g, b )
                time.sleep( 0.02 )
            upwardb = not upwardb
        upwardg = not upwardg

# -------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

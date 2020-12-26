#!/usr/bin/env python
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from enum import Enum
from i2c_device import I2C_Device

import time

__all__ = ['Grove_RGB_LCD_Size', 'Grove_RGB_LCD']

# =================================================================================================
class Grove_RGB_LCD_Size( Enum ):
    """! Seeed Studio Grove-LCD RGB Backlight Device Dot Sizes """
    SIZE_5x10_DOTS, SIZE_5x8_DOTS = range( 0, 2 )

# =================================================================================================
class Grove_RGB_LCD( object ):
    """! Seeed Studio Grove-LCD RGB Backlight Device (lcd JHD1313M3) """

    # this device has two I2C addresses
    LCD_I2C_ADDRESS = 0x3e
    RGB_I2C_ADDRESS = 0x62

    # color registers and modes
    REG_RED = 0x04                                  # pwm2
    REG_GREEN = 0x03                                # pwm1
    REG_BLUE = 0x02                                 # pwm0

    REG_MODE1 = 0x00
    REG_MODE2 = 0x01
    REG_OUTPUT = 0x08

    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00

    LCD_DOTS = {
        Grove_RGB_LCD_Size.SIZE_5x10_DOTS: 0x04,
        Grove_RGB_LCD_Size.SIZE_5x8_DOTS: 0x00,
    }

    # ---------------------------------------------------------------------------------------------
    def __init__( self, cols=16, rows=2, dotsize=Grove_RGB_LCD_Size.SIZE_5x8_DOTS ):
        """! Initialize Class
        @param cols  number of columns
        @param rows  number of rows (lines)
        @param dotsize  lcd dot size
        """

        # setup devices
        self.__lcd_dev = I2C_Device( self.LCD_I2C_ADDRESS )
        self.__rgb_dev = I2C_Device( self.RGB_I2C_ADDRESS )

        # setup
        self.numcols = cols
        self.numrows = rows

        if ( 1 < rows ):
            self.__function = self.LCD_2LINE
        else:
            self.__function = self.LCD_1LINE

        # for some 1 line displays you can select a 10 pixel high font
        if ( rows == 1 ):
            self.__function |= self.LCD_DOTS[dotsize]
        else:
            self.__function |= self.LCD_DOTS[Grove_RGB_LCD_Size.SIZE_5x8_DOTS]

        # send function set command sequence
        self.__command( self.LCD_FUNCTIONSET | self.__function )
        time.sleep( 0.0045 )                        # wait more than 4.1ms

        # second try
        self.__command( self.LCD_FUNCTIONSET | self.__function )
        time.sleep( 0.00015 )

        # third go
        self.__command( self.LCD_FUNCTIONSET | self.__function )

        # finally, set lines, font size, etc.
        self.__command( self.LCD_FUNCTIONSET | self.__function )

        # turn the display on with no cursor or blinking default
        self.__control = self.LCD_DISPLAYOFF | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.setDisplayEnabled( True )

        # clear it off
        self.clear()

        # initialize to default text direction (for romance languages)
        self.__entrymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT

        # set the entry mode
        self.__command( self.LCD_ENTRYMODESET | self.__entrymode )

        # backlight init
        self.__setReg( self.REG_MODE1, 0 )

        # set LEDs controllable by both PWM and GRPPWM registers
        self.__setReg( self.REG_OUTPUT, 0xFF )

        # set MODE2 values
        # 0010 0000 -> 0x20  (DMBLNK to 1, ie blinky mode)
        self.__setReg( self.REG_MODE2, 0x20 )

        # set color white
        self.setColor( 255, 255, 255 )

    # ---------------------------------------------------------------------------------------------
    def __setReg( self, addr, d ):
        """! Set Register Data
        @param addr  address
        @param d  data
        """
        self.__rgb_dev.writeReg( addr, d )

    # ---------------------------------------------------------------------------------------------
    def setBlink( self, enabled ):
        """! Control the backlight LED blinking
        @param enabled  @c True to enable, @c False otherwise
        """
        if ( enabled ):
            # blink period in seconds = (<reg 7> + 1) / 24
            # on/off ratio = <reg 6> / 256
            self.__setReg( 0x07, 0x17 )             # blink every second
            self.__setReg( 0x06, 0x7f )             # half on, half off
        else:
            self.__setReg( 0x07, 0x00 )
            self.__setReg (0x06, 0xff )

    # ---------------------------------------------------------------------------------------------
    def setColor( self, r, g, b ):
        """! Set Backlight Color
        Set backlight to (R,G,B) (values from 0..255 for each)
        @param r  red [0..255]
        @param g  green [0..255]
        @param b  blue [0..255]
        """
        self.__setReg( self.REG_RED, r )
        self.__setReg( self.REG_GREEN, g )
        self.__setReg( self.REG_BLUE, b )

    # ---------------------------------------------------------------------------------------------
    def __command( self, cmd ):
        """! Send command
        @param cmd  command
        """
        self.__lcd_dev.writeReg( 0x80, cmd )

    # ---------------------------------------------------------------------------------------------
    def setAutoScroll( self, enabled ):
        """! Setup auto scrolling
        @param enabled  @c True to 'right justify' text from the cursor, @c False to 'left justify' text from the cursor
        """
        if ( enabled ):
            self.__entrymode |= self.LCD_ENTRYSHIFTINCREMENT
        else:
            self.__entrymode &= ~self.LCD_ENTRYSHIFTINCREMENT

        self.__command( self.LCD_ENTRYMODESET | self.__entrymode )

    # ---------------------------------------------------------------------------------------------
    def setCursorBlink( self, enabled ):
        """! Turn on and off the blinking cursor
        @param enabled  @c True to enable, @c False otherwise
        """
        if ( enabled ):
            self.__control |= self.LCD_BLINKON
        else:
            self.__control &= ~self.LCD_BLINKON

        self.__command( self.LCD_DISPLAYCONTROL | self.__control )

    # ---------------------------------------------------------------------------------------------
    def setCursor( self, enabled ):
        """! Turns the underline cursor on/off
        @param enabled  @c True to enable, @c False otherwise
        """
        if ( enabled ):
            self.__control |= self.LCD_CURSORON
        else:
            self.__control &= ~self.LCD_CURSORON

        self.__command( self.LCD_DISPLAYCONTROL | self.__control )

    # ---------------------------------------------------------------------------------------------
    def setCursorPos( self, col, row ):
        """! Set cursor position
        @param col  cursor column
        @param row  cursor row
        """
        if ( row == 0 ):
            col |= 0x80
        else:
            col |= 0xc0

        self.__command( col )

    # ---------------------------------------------------------------------------------------------
    def setDisplayEnabled( self, enabled ):
        """! Turn the display on/off (quickly)
        @param enabled  @c True to enable display, @c False otherwise
        """
        if ( enabled ):
            self.__control |= self.LCD_DISPLAYON
        else:
            self.__control &= ~self.LCD_DISPLAYON

        self.__command( self.LCD_DISPLAYCONTROL | self.__control )

    # ---------------------------------------------------------------------------------------------
    def setLeftToRight( self, enabled ):
        """! This is for text that flows Left to Right
        @param enabled  @c True to enable, @c False otherwise
        """
        if ( enabled ):
            self.__entrymode |= self.LCD_ENTRYLEFT
        else:
            self.__entrymode &= ~self.LCD_ENTRYLEFT
    
        self.__command( self.LCD_ENTRYMODESET | self.__entrymode )

    # ---------------------------------------------------------------------------------------------
    def clear( self ):
        """! Clear display, set cursor position to zero """
        self.__command( self.LCD_CLEARDISPLAY )
        time.sleep( 0.002 );                        # this command takes a long time!

    # ---------------------------------------------------------------------------------------------
    def home( self ):
        """! Set cursor position to zero """
        self.__command( self.LCD_RETURNHOME )
        time.sleep( 0.002 );                        # this command takes a long time!

    # ---------------------------------------------------------------------------------------------
    def scrollDisplayLeft( self ):
        """! Scroll the display without changing the RAM """
        self.__command( self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT )

    # ---------------------------------------------------------------------------------------------
    def scrollDisplayRight( self ):
        """! Scroll the display without changing the RAM """
        self.__command( self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT )
 
    # ---------------------------------------------------------------------------------------------
    def createChar( self, location, charmap ):
        """! Allows us to fill the first 8 CGRAM locations with custom characters
        @param location  location [0-7]
        @param charmap  
        """
        if ( 8 == len(charmap) ):
            location &= 0x7                             # we only have 8 locations 0-7
            self.__command( self.LCD_SETCGRAMADDR | (location << 3) )

            self.__lcd_dev.writeBlockData( 0x40, charmap )

    # ---------------------------------------------------------------------------------------------
    def printText( self, text, wrap=False ):
        """! Print text (at current location)
        @param text  text to display
        @param wrap  @c True to wrap on 16th character or '\n', @c False otherwise
        """
        count = 0
        row = 0
        
        if ( wrap ):
            self.setCursorPos( count, row )

        for c in text:
            if ( wrap ):
                if (( c == '\n' ) or ( self.numcols <= count )):
                    count = 0
                    row += 1
                    if ( self.numrows <= row ):
                        break
                    self.setCursorPos( count, row )
                    if ( c == '\n' ):
                        continue
                count += 1

            if ( c <= 8 ):
                self.__lcd_dev.writeReg( 0x40, c )
            else:
                self.__lcd_dev.writeReg( 0x40, ord(c) )


# =================================================================================================
#
# Test Cases
#
# =================================================================================================

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

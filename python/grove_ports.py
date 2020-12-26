#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/rblankley/rpi-grove/blob/master/LICENSE
#

from enum import Enum

__all__ = ['Grove_Analog_Port', 'Grove_Digital_Port', 'Grove_Digital_Port_Direction']

# =================================================================================================
class Grove_Analog_Port( Enum ):
    """! Grove Analog Ports """
    A0, A1, A2, A3, A4, A5, A6, A7 = range( 0, 8 )

# =================================================================================================
class Grove_Digital_Port( Enum ):
    """! Grove Digital Ports """
    D0, D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D13, D14, D15, D16, D17, D18, D19, D20, D21, D22, D23, D24, D25, D26, D27, D28, D29, D30, D31 = range( 0, 32 )

# =================================================================================================
class Grove_Digital_Port_Direction( Enum ):
    """! Grove Digital Port Direction """
    INPUT, OUTPUT = range( 0, 2 )

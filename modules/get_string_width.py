# -*- coding: utf-8 -*-

import sys
import unicodedata

def getStringWidth(str=''):
    width = 0
    half = ['H', 'Na', 'N']
    for c in str:
        if sys.version_info.major < 3:
            uc = unicode(c)
        else:
            uc = c
        if unicodedata.east_asian_width(uc) in half:
            width += 1
        else:
            width += 2
    return width

# debug

# print(getStringWidth('あほ'))
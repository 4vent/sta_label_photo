# -*- coding: utf-8 -*-

import random
import colorsys

class rgb():
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.tuple = (r, g, b, a)

def getRandomColor(hMin=0, hMax=360, sMin=0, sMax=1, vMin=0, vMax=1, alpha=1.0):
    h = random.uniform(hMin, hMax)
    s = random.uniform(sMin, sMax)
    v = random.uniform(vMin, vMax)
    r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
    return rgb(r, g, b, alpha)

# -*- coding: utf-8 -*-

import ui

def createOneColorImage(x=10, y=10, r=0, g=0, b=0):
    with ui.ImageContext(x, y) as ctx:
        ui.set_color((r, g, b))
        ui.fill_rect(0, 0, x, y)
        img = ctx.get_image()
    return img

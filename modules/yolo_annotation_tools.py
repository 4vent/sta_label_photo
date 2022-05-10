# -*- coding: utf-8 -*-

def yoloPos2BoxPos(
    photoX,
    photoY,
    photoWidth,
    photoHeight,
    yoloCenterX,
    yoloCenterY,
    yoloWidth,
    yoloHeight
    ):
    return {
        'x': float(yoloCenterX) * photoWidth + photoX,
        'y': float(yoloCenterY) * photoHeight + photoY,
        'width': float(yoloWidth) * photoWidth,
        'height': float(yoloHeight) * photoHeight
    }

def boxPos2YoloPos(
    photoX,
    photoY,
    photoWidth,
    photoHeight,
    boxCenterX,
    boxCenterY,
    boxWidth,
    boxHeight
    ):
    return {
        'x': (boxCenterX - photoX) / float(photoWidth),
        'y': (boxCenterY - photoY) / float(photoHeight),
        'width': boxWidth / float(photoWidth),
        'height': boxHeight / float(photoHeight)
    }

def makeYoloAnotationLine(labelIndex, photo, boxView):
    yoloLine = boxPos2YoloPos(
        photo['x'],
        photo['y'],
        photo['width'],
        photo['height'],
        boxView.center[0],
        boxView.center[1],
        boxView.width,
        boxView.height
        )

    begenX = yoloLine['x'] - yoloLine['width'] / 2
    if begenX < 0:
        yoloLine['width'] += begenX
        yoloLine['x'] += -begenX / 2
    
    begenY = yoloLine['y'] - yoloLine['height'] / 2
    if begenY < 0:
        yoloLine['height'] += begenY
        yoloLine['y'] += -begenY / 2
    
    finishX = yoloLine['x'] + yoloLine['width'] / 2
    if finishX > 1:
        yoloLine['width'] -= finishX - 1
        yoloLine['x'] -= (finishX - 1) / 2
    
    finishY = yoloLine['y'] + yoloLine['height'] / 2
    if finishY > 1:
        yoloLine['height'] -= finishY - 1
        yoloLine['y'] -= (finishY - 1) / 2
        
    
    return '{} {:.6f} {:.6f} {:.6f} {:.6f}'.format(labelIndex, yoloLine["x"], yoloLine["y"], yoloLine["width"], yoloLine["height"])

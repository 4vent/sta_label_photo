# -*- coding: utf-8 -*-

import ui
import photos
import dialogs
import console
from objc_util import ObjCInstance, on_main_thread
import os
import sys
import json
import math
import random
import time
import unicodedata

sys.path.append('modules')

import config
from config import slideBarView
from ease import Ease
from compair_strings import compairString
from get_string_width import getStringWidth
from yolo_annotation_tools import yoloPos2BoxPos, boxPos2YoloPos, makeYoloAnotationLine
from pythonista_photos_tools import getSortedAlbums, getAlbumWithDialog
from random_color_generator import getRandomColor
from pythonista_ui_tools import createOneColorImage

themeColors = config.theme_colors
ancorGuideNames = config.ancore_guid_names

### ------------- ###
### Global Values ###
### ------------- ###

v = ui.View()

is2PColor = False
selectedThemeIndex = 0

selectedAncor = 'tl'
ancorHitboxSize = 5
imgOffset = {}

boxCount = 0
boxData = {}
selectedBox = None
selectedBoxIndex = 0

imageLastPos = (0,0)
trueImageLastPos = (0,0)
touchBeganPos = (0,0)
lastTouchLocation = (0,0)
activeTouchIDs = {}

lastScale = 1.0
trueLastScale = 1.0
initialImageScale = (0, 0)
lastSliderValue = 0
pinchBeganDistance = 0.0
zoom_mode = True

showingImage = 

vrt_hitbox = ui.Path
hlz_hitbox = ui.Path

centerPos = (0,0)
padding = 6


assets = []
photoNum = 0
isEdited = False
classes = []
selectedLabelIndex = 0

isAncorEditing = False
lastTouchTimestamp = 0
doubleTouchFlag = False
multiTouchFlag = False
hittingSlideBarView = slideBarView.notthing
trueLastTouchLocation = (0,0)

menu_state = False
nowThemeNum = 0

### ------- ###
### classes ###
### ------- ###

class labelClass():
    def __init__(self, title, bgcolor, textcolor):
        self.title = title
        self.bgcolor = bgcolor
        self.textcolor = textcolor

### ---------------------------------------- ###
### Standalone Tools (but use global values) ###
### ---------------------------------------- ###

def applyThemeColor(index, isSingleContent=False, contentType=None, content=None, isSelectedBox=True):
    global themeColors
    global boxCount
    global selectedBox
    global selectedThemeIndex
    
    selectedThemeIndex = index
    
    # guide
    if not isSingleContent or contentType == 'guideBox':
        c = content if isSingleContent else v['guidBox']
        c.border_color = themeColors[index]['guide']
    
    if not isSingleContent: 
        if boxCount == 0:
            return
        for i in range(boxCount):
            v['Image']['rangeBox' + str(i)].border_color = themeColors[index]['box']
            v['Image']['rangeBox' + str(i)].border_width = config.deselected_border_width
            v['Image']['rangeBox' + str(i)].background_color = themeColors[index]['boxbg']
            for view in v['Image']['rangeBox' + str(i)].subviews:
                if not view.name.startswith('ancorDot'):
                    continue
                view.background_color = (0,0,0,0)
    
    # selectedBox
    if not isSingleContent:
        if boxCount == 0:
            return
        selectedBox.border_color = themeColors[index]['selectedbox']
        selectedBox.border_width = config.selected_border_width
        selectedBox.background_color = themeColors[index]['selectedboxbg']
        for view in selectedBox.subviews:
            if not view.name.startswith('ancorDot'):
                continue
            view.background_color = themeColors[index]['selectedbox']

    if isSingleContent and contentType == 'box':
        boxColor = 'selectedbox' if isSelectedBox else 'box'
        boxBGcolor = 'selectedboxbg' if isSelectedBox else 'boxbg'
        content.border_color = themeColors[index][boxColor]
        content.background_color = themeColors[index][boxBGcolor]
        content.border_width = config.selected_border_width if isSelectedBox else config.deselected_border_width
        for view in content.subviews:
            if not view.name.startswith('ancorDot'):
                continue
            view.background_color = themeColors[index][boxColor] if isSelectedBox else (0,0,0,0)

### ------------------------- ###
### Controle Ancore Functions ###
### ------------------------- ###

def createAncorGuide():
    global ancorGuideNames
    global v
    for agn in ancorGuideNames:
        view = ui.View(frame=(0,0,100,100), background_color=(0.5, 0.5, 0.5, 0.3), name=agn)
        view.corner_radius = 50
        view.alpha = 0.0
        v['ancor_guide_layer'].add_subview(view)

def getAncorsPos():
    global boxData
    global v
    global imgOffset
    offsetY = imgOffset['y']
    return (
        (boxData['x']                   , offsetY + boxData['y']                   ), # tl
        (boxData['x'] + boxData['w'] / 2, offsetY + boxData['y']                   ), # tm
        (boxData['x'] + boxData['w']    , offsetY + boxData['y']                   ), # tr
        (boxData['x']                   , offsetY + boxData['y'] + boxData['h'] / 2), # ml
        (boxData['x'] + boxData['w']    , offsetY + boxData['y'] + boxData['h'] / 2), # mr
        (boxData['x']                   , offsetY + boxData['y'] + boxData['h']    ), # bl
        (boxData['x'] + boxData['w'] / 2, offsetY + boxData['y'] + boxData['h']    ), # bm
        (boxData['x'] + boxData['w']    , offsetY + boxData['y'] + boxData['h']    ), # br
        (boxData['x'] + boxData['w'] / 2, offsetY + boxData['y'] + boxData['h'] / 2), # center
        )

def updateAncorGuid():
    global boxCount
    if boxCount == 0:
        return
    ancorsPos = getAncorsPos()
    global ancorGuideNames
    global ancorHitboxSize
    for i,agn in enumerate(ancorGuideNames):
        v['ancor_guide_layer'][agn].center = ancorsPos[i]
        v['ancor_guide_layer'][agn].width = ancorHitboxSize * 2
        v['ancor_guide_layer'][agn].height = ancorHitboxSize * 2
        v['ancor_guide_layer'][agn].corner_radius =  ancorHitboxSize

def setAncorValue(box):
    global v
    global boxAncors
    global boxData
    
    if not box:
        return 
    
    boxData = {
        'x': box.x + v['Image'].x,
        'y': box.y + v['Image'].y,
        'absx': box.x,
        'absy': box.y,
        'w': box.width,
        'h': box.height
    }
    updateAncorGuid()
    # print(boxData)

def moveAncor(touch):
    global boxData
    global touchBeganPos
    global selectedAncor
    dpos = [b-a for (a, b) in zip(touchBeganPos, touch.location)]
    
    if selectedAncor in ['tl', 'tr', 'tm']:
        selectedBox.y = boxData['absy'] + min(dpos[1], boxData['h'])
        selectedBox.height = max(boxData['h'] - dpos[1], 1)
    if selectedAncor in ['bl', 'br', 'bm']:
        selectedBox.height = max(boxData['h'] + dpos[1], 1)
    if selectedAncor in ['tl', 'bl', 'ml']:
        selectedBox.x = boxData['absx'] + min(dpos[0], boxData['w'])
        selectedBox.width = max(boxData['w'] - dpos[0], 1)
    if selectedAncor in ['tr', 'br', 'mr']:
        selectedBox.width = max(boxData['w'] + dpos[0], 1)
    if selectedAncor in ['center']:
        selectedBox.y = boxData['absy'] + dpos[1]
        selectedBox.x = boxData['absx'] + dpos[0]
    
    doZoomGlass(touch.location, 'photoPos', 'photoScale')

def getNearestAncor(touch):
    global boxCount
    global ancorHitboxSize
    if boxCount == 0:
        return False
    global selectedAncor
    flag = False
    ancors = getAncorsPos()
    minDistance = ancorHitboxSize
    
    for i, ancor in enumerate(ancors):
        d = math.sqrt(sum([(a-b) ** 2 for (a, b) in zip(touch.location, ancor)]))
        if d < minDistance:
            minDistance = d
            ancornames = ['tl', 'tm', 'tr', 'ml', 'mr', 'bl', 'bm', 'br', 'center']
            selectedAncor = ancornames[i]
            flag = True
            
    return flag

def showAncorGuid():
    global v
    if not v['show_ancor_guid_switch'].value:
        return
    global ancorGuideNames
    global boxCount
    if boxCount == 0:
        return
    for agn in ancorGuideNames:
        v['ancor_guide_layer'][agn].alpha = 1.0

def hideAncorGuid():
    global ancorGuideNames
    for agn in ancorGuideNames:
        v['ancor_guide_layer'][agn].alpha = 0.0

### --------------------------- ###
### Label Box Control Functions ###
### --------------------------- ###

def createNewBox(labelNum=None, center=None, width=None, height=None):
    # print('create new box(title = {}, center = {}, width = {}, height = {})'.format(labelTitle, center, width, height))
    global boxCount
    global v
    global centerPos
    global themeColors
    global selectedThemeIndex
    
    box = ui.View(flex = '')
    box.border_width = 2
    ancorDotSize = 5
    ancorDots = [
        ui.View(frame=(0,0,ancorDotSize,ancorDotSize), flex='RB', name='ancorDot0'),
        ui.View(frame=(50-ancorDotSize/2,0,ancorDotSize,ancorDotSize), flex='LRB', name='ancorDot1'),
        ui.View(frame=(100-ancorDotSize,0,ancorDotSize,ancorDotSize), flex='LB', name='ancorDot2'),
        ui.View(frame=(0,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='RTB', name='ancorDot3'),
        ui.View(frame=(100-ancorDotSize,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='LTB', name='ancorDot4'),
        ui.View(frame=(0,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='RT', name='ancorDot5'),
        ui.View(frame=(50-ancorDotSize/2,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='LRT', name='ancorDot6'),
        ui.View(frame=(100-ancorDotSize,100-ancorDotSize,ancorDotSize,ancorDotSize), flex='LT', name='ancorDot7'),
        ui.View(frame=(50-ancorDotSize/2,50-ancorDotSize/2,ancorDotSize,ancorDotSize), flex='LRTB', name='ancorDot8'),
        ]
    
    for d in ancorDots:
        box.add_subview(d)
    box.flex = 'WHLRTB'
    box.name = 'rangeBox' + str(boxCount)
    
    # global labelColors
    global classes
    label = ui.Label(name='label', flex='RB')
    if labelNum == None or labelNum >= len(classes):
        label.text = 'Error'
        label.background_color = (0,0,0,0.4)
        label.text_color = (1,1,1)
    else:  
        label.text = classes[labelNum].title
        label.background_color = classes[labelNum].bgcolor.tuple
        label.text_color = classes[labelNum].textcolor
    label.alignment = ui.ALIGN_CENTER
    label.x, label.y = 0, 0
    label.height = 18
    stringWidth = getStringWidth(label.text)
    label.width = stringWidth * 9
    label.scales_font = True
    
    applyThemeColor(
        selectedThemeIndex,
        isSingleContent = True,
        contentType = 'box',
        content = box,
        isSelectedBox = True
        )
    box.add_subview(label)
    
    if center and width and height:
        box.width = width
        box.height = height
        box.center = center
    else:
        box.bounds = (0,0,200,200)
        imageViewCenterGap = [a-b for (a, b) in zip(v['Image'].center, centerPos)]
        centerPosInImageView = (v['Image'].width / 2, v['Image'].height / 2)
        box.center = [a-b for (a, b) in zip(centerPosInImageView, imageViewCenterGap)]
    # print('add_subview(height={}, width={})'.format(box.height, box.width))
    v['Image'].add_subview(box)
    boxCount += 1
    selectBox(boxCount - 1)

def selectBox(index):
    global selectedBox
    global selectedBoxIndex
    global v
    global themeColors
    global selectedThemeIndex
    
    if boxCount == 0:
        return 
    
    selectedBoxIndex = index
    
    if selectedBox:
        applyThemeColor(
            selectedThemeIndex,
            isSingleContent = True,
            contentType = 'box',
            content = selectedBox,
            isSelectedBox = False
            )
    selectedBox = v['Image']['rangeBox' + str(index)]
    applyThemeColor(
        selectedThemeIndex,
        isSingleContent = True,
        contentType = 'box',
        content = selectedBox,
        isSelectedBox = True
        )
    
    setAncorValue(selectedBox)

def clearAllBox():
    global v
    global boxCount
    for i in range(boxCount):
        v['Image'].remove_subview(v['Image']['rangeBox' + str(i)])
    boxCount = 0

### ----------------------- ###
### Display Touch Functions ###
### ----------------------- ###

### Touch Controle Class ###

class touchView(ui.View):
    def touch_began(self, touch):
        global isAncorEditing
        global lastTouchTimestamp
        global doubleTouchFlag
        global activeTouchIDs
        global multiTouchFlag
        global hittingSlideBarView
        activeTouchIDs[touch.touch_id] = touch.location
        
        global trueLastTouchLocation
        trueLastTouchLocation = touch.location
        
        if lastTouchTimestamp + 0.25 > touch.timestamp:
            doubleTouchFlag = True
            setLastZoomScale()
        lastTouchTimestamp = touch.timestamp
        if getNearestAncor(touch):
            isAncorEditing = True
            showZoomGlass()
            global isEdited
            isEdited = True
        else:
            setImageLastPos()
        
        if len(activeTouchIDs) == 2:
            multiTouchFlag = True
            setTouchBeganPos(getPinchCenterPos())
            global pinchBeganDistance
            pinchBeganDistance = getPinchDistance()
            setLastZoomScale()
        else:
            setTouchBeganPos(touch.location)
        hideAncorGuid()
        
        global hittingSlideBarView
        global vrt_hitbox
        global hlz_hitbox
        global slideBarView
        if vrt_hitbox.hit_test(*touch.location):
            hittingSlideBarView = slideBarView.vertical
        elif hlz_hitbox.hit_test(*touch.location):
            hittingSlideBarView = slideBarView.holizontal
        
    def touch_moved(self, touch):
        global isAncorEditing
        global doubleTouchFlag
        global activeTouchIDs
        global multiTouchFlag
        activeTouchIDs[touch.touch_id] = touch.location
        if lastTouchTimestamp + 0.08 < touch.timestamp:
            if multiTouchFlag:
                if len(activeTouchIDs) == 2:
                    pinch()
            elif doubleTouchFlag:
                zoomWithDoubletouch(touch)
            elif isAncorEditing:
                moveAncor(touch)
            else:
                global hittingSlideBarView
                global slideBarView
                if hittingSlideBarView == slideBarView.vertical:
                    moveImage(touch.location, canMove='vertical')
                elif hittingSlideBarView == slideBarView.holizontal:
                    moveImage(touch.location, canMove='horizontal')
                else:
                    moveImage(touch.location)
        
    def touch_ended(self, touch):
        global isAncorEditing
        global selectedBox
        global doubleTouchFlag
        global selectedAncor
        global multiTouchFlag
        if boxCount > 0:
            pass
            # selectBox()
        del activeTouchIDs[touch.touch_id]
        if len(activeTouchIDs) == 0:
            multiTouchFlag = False
        isAncorEditing = False
        doubleTouchFlag = False
        selectedAncor = None
        showAncorGuid()
        hideZoomGlass()
        
        global hittingSlideBarView
        global slideBarView
        hittingSlideBarView = slideBarView.notthing
        
        setAncorValue(selectedBox)

### Move Functions ###

def setImageLastPos():
    global v
    global imageLastPos
    global trueImageLastPos
    global trueLastScale
    global lastScale
    imageLastPos = v['Image'].center
    trueImageLastPos = v['Image'].center
    trueLastScale = lastScale

def setTouchBeganPos(location):
    global touchBeganPos
    global lastTouchLocation
    touchBeganPos = location
    lastTouchLocation = location

def moveImage(location, canMove='notthing'):
    global imageLastPos
    global touchBeganPos
    global lastTouchLocation
    global trueLastTouchLocation
    
    mgn = 200
    
    dpos = [da-a for (a, da) in zip(lastTouchLocation, location)]
    
    tDpos = [da-a for (a, da) in zip(trueLastTouchLocation, location)]
    
    if canMove == 'horizontal':
        dx = dpos[0] * Ease.inSine(1.0/2, 1.0/16, abs(tDpos[1])/mgn)
        v['Image'].center += (dx, 0)
    elif canMove == 'vertical':
        dy = dpos[1] * Ease.inSine(1.0/2, 1.0/16, abs(tDpos[0])/mgn)
        v['Image'].center += (0, dy)
    else:
        v['Image'].center += dpos
    lastTouchLocation = location

### Zoom Functions ###

def setLastZoomScale():
    global lastSliderValue
    lastSliderValue = v['slider_zoom'].value

def imageZoom(zoomCenter, scale, isUpdateSlider=False):
    global v
    global initialImageScale
    global lastScale
    global ancorHitboxSize
    global imageLastPos
    ancorHitboxSize = min(Ease.inSine(10,200,v['slider_zoom'].value), 70)
    v['Image'].height, v['Image'].width = initialImageScale[0] * scale, initialImageScale[1] * scale
    v['Image'].x -= (scale / lastScale - 1) * (zoomCenter[0] - v['Image'].x)
    v['Image'].y -= (scale / lastScale - 1) * (zoomCenter[1] - v['Image'].y)
    imageLastPos = (
        (imageLastPos[0] - zoomCenter[0]) * (scale / lastScale) + zoomCenter[0],
        (imageLastPos[1] - zoomCenter[1]) * (scale / lastScale) + zoomCenter[1]
        )
    lastScale = scale
    
    global boxCount
    if not boxCount == 0:
        global selectedBox
        setAncorValue(selectedBox)
        
    if isUpdateSlider:
        v['slider_zoom'].value = Ease.inQuad_inverse(1, 16, scale)

def imageZoomBySliderValue(zoomCenter):
    scale = Ease.inQuad(1, 16, v['slider_zoom'].value)
    imageZoom(zoomCenter, scale)

def zoomWithDoubletouch(touch):
    global touchBeganPos
    global lastSliderValue
    global zoom_mode
    global v
    global centerPos
    coef = 800
    dy = touch.location[1] - touchBeganPos[1]
    v['slider_zoom'].value = lastSliderValue + dy / coef
    if zoom_mode:
        imageZoomBySliderValue(touchBeganPos)
    else:
        imageZoomBySliderValue(centerPos)

def getPinchCenterPos():
    global activeTouchIDs
    center = (
        (dict(activeTouchIDs).values()[0][0] + dict(activeTouchIDs).values()[1][0]) / 2,
        (dict(activeTouchIDs).values()[0][1] + dict(activeTouchIDs).values()[1][1]) / 2
    )
    return center

def getPinchDistance():
    global activeTouchIDs
    distance = math.sqrt(
        (dict(activeTouchIDs).values()[0][0] - dict(activeTouchIDs).values()[1][0]) ** 2 +
        (dict(activeTouchIDs).values()[0][1] - dict(activeTouchIDs).values()[1][1]) ** 2
    )
    return distance

def pinch():
    global v
    global pinchBeganDistance
    global lastSliderValue
    global trueLastScale
    center = getPinchCenterPos()
    pinchDistance = getPinchDistance()
    zoomRate = (pinchDistance / pinchBeganDistance)
    imageZoom(center, trueLastScale * zoomRate, isUpdateSlider=True)
    #if zoomRate < 1:
    #    v['slider_zoom'].value = lastSliderValue - Ease.inQuad_inverse(1, 16, 1/zoomRate)
    #else:
    #    v['slider_zoom'].value = lastSliderValue + Ease.inQuad_inverse(1, 16, zoomRate)
    moveImage(center)
    imageZoomBySliderValue(center)

### --------------------------------- ###
### Progress Label Controle Functions ###
### --------------------------------- ###

@on_main_thread
def initProgressLabel():
    v['progress_label'].background_color = (1.0, 1.0, 1.0, 0.7)
    v['progress_label'].corner_radius = 16
    ObjCInstance(v['progress_label']).clipsToBounds = True

def updateProgressLabel():
    global v
    global photoNum
    global assets
    v['progress_label'].text = '{}/{}'.format(photoNum+1, len(assets))

### ------------------------------------- ###
### Create Yolo Annotation File Functions ###
### ------------------------------------- ###

def getPhotoPosAndScale():
    global photoNum
    global assets
    photo = assets[photoNum]
    
    imageViewVerticalRatio = v['Image'].height / v['Image'].width
    photoVerticalRatio = photo.pixel_height / photo.pixel_width
    
    if imageViewVerticalRatio > photoVerticalRatio: # 上下余白の場合
        mag = v['Image'].width / photo.pixel_width # 倍率
        return {
            'x': 0,
            'y': (v['Image'].height - (photo.pixel_height * mag)) / 2,
            'width': v['Image'].width,
            'height': photo.pixel_height * mag
        }
    else:                                           # 左右余白の場合
        mag = v['Image'].height / photo.pixel_height # 倍率
        return {
            'y': 0,
            'x': (v['Image'].width - (photo.pixel_width * mag)) / 2,
            'height': v['Image'].height,
            'width': photo.pixel_width * mag
        }

### ----------------------------- ###
### Direction Slide Bar Functions ###
### ----------------------------- ###

def initSlideBarView():
    global v
    global vrt_hitbox
    global hlz_hitbox
    
    vrt = v['vertical_slide_bar_view']
    hlz = v['holizontal_slide_bar_view']
    
    vrt.touch_enabled, hlz.touch_enabled = False, False
    
    ObjCInstance(vrt).clipsToBounds, ObjCInstance(hlz).clipsToBounds = True, True
    
    vrt.corner_radius, hlz.corner_radius = 16, 16
    
    vrt.background_color, hlz.background_color = (0.5, 0.5, 0.5, 0.3), (0.5, 0.5, 0.5, 0.3)
    
    vrt.text, hlz.text = '', ''
    
    vrt_hitbox = ui.Path.rect(
        vrt.x,
        vrt.y,
        vrt.width,
        vrt.height
        )
    hlz_hitbox = ui.Path.rect(
        hlz.x,
        hlz.y,
        hlz.width,
        hlz.height
        )

### ------------------------------- ###
### Overlay HSV Controler Functions ###
### ------------------------------- ###

def initOverlaySystem():
    global v
    global centerPos
    global padding
    saturationScreen = ui.View(frame=v['Image'].bounds ,flex='WH', name='saturationScreen')
    brightnessScreen = ui.View(frame=v['Image'].bounds ,flex='WH', name='brightnessScreen')
    
    saturationScreen.background_color = 'white'
    brightnessScreen.background_color = 'black'
    
    saturationScreen.alpha = 0.0
    brightnessScreen.alpha = 0.0
    
    v['Image'].add_subview(saturationScreen)
    v['Image'].add_subview(brightnessScreen)
    
    ss = v['saturation_slider']
    bs = v['brightness_slider']
    
    ss.continuous = True
    bs.continuous = True
    
    sliderLeftX = ss.x
    sliderRightX = bs.x + bs.width
    
    width = (sliderRightX - sliderLeftX) / 2 - padding / 2
    
    ss.width = width
    bs.width = width
    
    bs.x = (sliderRightX + sliderLeftX) / 2 + padding / 2

### ----------------- ###
### UI Style Function ###
### ----------------- ###

def initUIItems():
    global v
    v['button_done'].alignment = ui.ALIGN_RIGHT

### ------------- ###
### menu function ###
### ------------- ###

def initMenuView():
    global v
    menu = ui.load_view('menu.pyui')
    menu.width = v['menu_view'].width
    menu.height = v['menu_view'].height
    menu.flex = 'WH'
    menu.name = 'menu'
    menu.background_color = (1,1,1,0.8)
    v['menu_view'].add_subview(menu)
    
def openMenue():
    global v
    global menu_state
    
    bgView = ui.Button(name='menuBG')
    bgView.background_color = (0,0,0,1)
    bgView.bounds = v['touch_panel'].bounds
    bgView.x, bgView.y = 0, 0
    bgView.alpha = 0
    bgView.action = onButtonMenu
    
    def animation():
        v['menu_view'].x -= v['menu_view'].width
        v['menuBG'].alpha = 0.7
    
    v.add_subview(bgView)
    v['menu_view'].bring_to_front()
    v['button_menu'].bring_to_front()
    ui.animate(animation, 0.25)
    
    menu_state = True
    
    
    
def closeMenue():
    global v
    global menu_state
    
    def animation():
        v['menu_view'].x += v['menu_view'].width
        v['menuBG'].alpha = 0
        
    def completion():
        v.remove_subview(v['menuBG'])
    
    ui.animate(animation, 0.25, completion=completion)
    
    menu_state = False
    
### -------------------- ###
### Zoom glass functions ###
### -------------------- ###

def showZoomGlass():
    global v
    v['glass_image_view'].alpha = 1
    
def hideZoomGlass():
    global v
    v['glass_image_view'].alpha = 0

def doZoomGlass(touchPos, photoPos, photoScale):
    global v
    global photoNum
    global assets
    
    if touchPos[0] > v['touch_panel'].width / 2:
        v['glass_image_view'].x = 0
    else:
        v['glass_image_view'].x = v['touch_panel'].width - v['glass_image_view'].width
    
    if touchPos[1] > v['touch_panel'].height / 2:
        v['glass_image_view'].y = 0
    else:
        v['glass_image_view'].y = v['touch_panel'].height - v['glass_image_view'].height
        
    assets[photoNum].get_image() as img:
        data = 'io.BytesIO'
        img.save(data, 'JPEG')
        v['glass_image_view'].image = ui.Image.from_data(data)
    
    

### --------------------------------- ###
### Read and Write and Draw Functions ###
### --------------------------------- ###

def loadClassesFile():
    global classes
    classes = []
    with open('result/classes.txt', 'r') as f:
        classTitles = f.read().split()
    
    colorOffset = random.uniform(0, 360)
    for c in classTitles:
        color = getRandomColor(hMin=colorOffset, hMax=colorOffset+40, sMin=0.6, vMin=0.5, vMax=0.7, alpha=0.8)
        # print(rgb)
        light = 0.9
        textcolor = (
            color.r + (1-color.r) * light,
            color.g + (1-color.g) * light,
            color.b + (1-color.b) * light,
            )
        classes.append(labelClass(c, color, textcolor))
        colorOffset += 80
        if not colorOffset < 360:
            colorOffset -= 360


def reloadClasses():
    global v
    global classes
    
    prevClasses = [c.title for c in classes]
    
    loadClassesFile()
    
    boxes = v['Image'].subviews
    avoidViewNames = ['saturationScreen', 'brightnessScreen']
    for box in boxes:
        if box.name in avoidViewNames:
            continue
        classIndex = prevClasses.index(box['label'].text)
        title = classes[classIndex].title
        box['label'].text = title
        print(classes[classIndex].title)
        box['label'].background_color = classes[classIndex].bgcolor.tuple
        box['label'].width = getStringWidth(title) * 9

def saveClassesFile():
    global classes
    classTitles = []
    for c in classes:
        classTitles.append(c.title)
    with open('result/classes.txt', 'w') as f:
        f.write('\n'.join(classTitles))

def loadAnnotationFile():
    global assets
    global photoNum
    
    photoAsset = assets[photoNum]
    
    photoFileName = str(ObjCInstance(photoAsset).filename())
    annotationFileName = os.path.splitext(photoFileName)[0] + '.txt'
    
    if not os.path.exists('result/' + annotationFileName):
        return
    
    photoInImageView = getPhotoPosAndScale()
    lines = []
    with open('result/' + annotationFileName)  as f:
        lines = f.readlines()
    
    for line in lines:
        args = line.split(' ')
        box = yoloPos2BoxPos(
            photoInImageView['x'],
            photoInImageView['y'],
            photoInImageView['width'],
            photoInImageView['height'],
            float(args[1]),
            float(args[2]),
            float(args[3]),
            float(args[4])
            )
        createNewBox(
            labelNum=int(args[0]),
            center=(box['x'], box['y']),
            width=box['width'],
            height=box['height']
            )

def saveAnnotation(isNotice = False):
    global boxCount
    global photoNum
    global assets
    
    global isEdited
    if not isEdited:
        return 
    
    if boxCount == 0:
        return
    
    photoAsset = assets[photoNum]
    photoFileName = str(ObjCInstance(photoAsset).filename())
    
    annotationFileName = os.path.splitext(photoFileName)[0] + '.txt'
    
    if os.path.exists('result/' + annotationFileName):
        yesOrNo = console.alert('ファイルが存在します。', '上書きしますか？', 'はい', 'いいえ', hide_cancel_button=True)
        if yesOrNo == 2:
            return
            
    photoInImageView = getPhotoPosAndScale()
    
    yoloAnotationText = ''
    classTitles = [c.title for c in classes]
    for i in range(boxCount):
        boxView = v['Image']['rangeBox' + str(i)]
        labelIndex = classTitles.index(boxView['label'].text)
        line = makeYoloAnotationLine(labelIndex, photoInImageView, boxView)
        
        yoloAnotationText += line + '\n'
    
    with open('result/' + annotationFileName, 'w') as f:
        f.write(yoloAnotationText)

def openImage():
    global photoNum
    global assets
    global centerPos
    global showingImage
    global v
    
    v['slider_zoom'].value = 0
    imageZoomBySliderValue(centerPos)
    v['Image'].center = centerPos
    clearAllBox()
    showingImage = assets[photoNum].get_ui_image()
    v['Image'].image = showingImage
    with open('lastedited.json', 'r') as f:
        lastedited = json.load(f)
        lastedited['assetid'] = assets[photoNum].local_id
    with open('lastedited.json', 'w') as f:
        json.dump(lastedited, f)
    updateProgressLabel()
    
    loadAnnotationFile()
    
    global isEdited
    isEdited = False
    
    global selectedLabelIndex
    selectedLabelIndex = 0

def openNextImage():
    global photoNum
    global assets
    if photoNum == len(assets) - 1:
        dialogs.alert('最新の写真です。', button1='OK', hide_cancel_button=True)
    else:
        photoNum += 1
    openImage()

def openPrevImagee():
    global photoNum
    global assets
    if photoNum == 0:
        dialogs.alert('最初の写真です',  button1='OK', hide_cancel_button=True)
    else:
        photoNum -= 1
    openImage()

def setPhotoNumByPickAssets(assets):
    global photoNum
    selectedAsset = photos.pick_asset(assets)
    if not selectedAsset:
        return
    photoNum = assets.index(selectedAsset)

def openLastEdetedFile():
    global assets
    global photoNum
    with open('lastedited.json', 'r') as f:
        lastEditing = json.loads(f.read())
        if not 'albumid' in lastEditing:
            return False
        LEAlbumID = lastEditing['albumid']
        albums = photos.get_albums()
        if not LEAlbumID in [a.local_id for a in albums]:
            return False
        albumIndex = [a.local_id for a in albums].index(LEAlbumID)
        assets = albums[albumIndex].assets
        if config.is_assets_reverse:
            assets.reverse()
        if not 'assetid' in lastEditing:
            return False
        LEAssetID = lastEditing['assetid']
        if not LEAssetID in [a.local_id for a in assets]:
            return False
        photoNum = [a.local_id for a in assets].index(LEAssetID)
        openImage()
        return True

def openPhotoBySelectPhoto():
    global assets
    selectedAlbum = getAlbumWithDialog()
    with open('lastedited.json', 'r') as f:
        lastedited = json.load(f)
        lastedited['albumid'] = selectedAlbum.local_id
    with open('lastedited.json', 'w+') as f:
        json.dump(lastedited, f)
        
    assets = selectedAlbum.assets
    if config.is_assets_reverse:
        assets.reverse()
    setPhotoNumByPickAssets(assets)
    openImage()

### ---------------- ###
### on ~~~ Functions ###
### ---------------- ###

def onSliderZoom(_):
    global centerPos
    imageZoomBySliderValue(centerPos)

def onButtonCreate(_):
    global selectedLabelIndex
    createNewBox(labelNum=selectedLabelIndex)
    global isEdited
    isEdited = True

def onButtonDone(_):
    saveAnnotation()
    openNextImage()

def onButtonBack(_):
    saveAnnotation()
    openPrevImagee()

def onButtonSelect(_):
    saveAnnotation(isNotice=True)
    closeMenue()
    openPhotoBySelectPhoto()

def onButtonDelete(_):
    global boxCount
    global v
    if boxCount == 0:
        return
    v['Image'].remove_subview(selectedBox)
    
    j = 0
    for i in range(boxCount):
        box = v['Image']['rangeBox'+str(i)]
        if box == None:
            continue
        else:
            box.name = 'rangeBox'+str(j)
            j += 1
    
    boxCount -= 1
    if boxCount == 0:
        return
    
    selectBox(boxCount-1)
    
    global isEdited
    isEdited = True

def onSwitchShowAncorGuid(sender):
    global boxCount
    if sender.value:
        if not boxCount == 0:
            setAncorValue(selectedBox)
            showAncorGuid()
    else:
        hideAncorGuid()

def onButtonTheme(_):
    global nowThemeNum
    global config
    nowThemeNum += 1
    if nowThemeNum == len(config.theme_colors):
        nowThemeNum = 0
    applyThemeColor(nowThemeNum)

def onSaturationSlider(sender):
    v['Image']['saturationScreen'].alpha = sender.value

def onBrightnessSlider(sender):
    val = sender.value
    v['Image']['brightnessScreen'].alpha = val
    v.background_color = (1-val, 1-val, 1-val)

def onButtonChangeSelect(_):
    global selectedBoxIndex
    global boxCount
    
    index = selectedBoxIndex + 1
    if index == boxCount:
        index = 0
    
    selectBox(index)

def onButtonChooseLabel(_):
    global classes
    items = []
    for c in classes:
        r, g, b = c.bgcolor.r, c.bgcolor.g, c.bgcolor.b
        items.append({
            'title': c.title,
            'image': createOneColorImage(x=200, y=200, r=r, g=g, b=b)
        })
    selectedLabel = dialogs.list_dialog(items=items)
    if selectedLabel == None:
        return
    index = [c.title for c in classes].index(selectedLabel['title'])
    
    global selectedBox
    selectedBox['label'].text = classes[index].title
    selectedBox['label'].background_color = (classes[index].bgcolor.tuple)
    
    global selectedLabelIndex
    selectedLabelIndex = index
    
    global isEdited
    isEdited = True

def onButtonEditClasses(_):
    global ges
    global classes
    prevClasses = [c.title for c in classes]
    
    import edit_classes
    edit_classes.choose_class_dialog()
    reloadClasses()
    closeMenue()

@ui.in_background  
def onButtonDelPhoto(_):
    global assets
    global v
    global photoNum
    
    tmp = ui.View(name='tmp')
    tmp.width, tmp.height = v['touch_panel'].width, v['touch_panel'].height
    v.add_subview(tmp)
    
    asset = assets[photoNum]
    photos.batch_delete([asset])
    
    v.remove_subview(v['tmp'])
    
    openNextImage()
    openLastEdetedFile()
    
    closeMenue()
    
def onButtonMenu(_):
    global menu_state
    if menu_state:
        closeMenue()
    else:
        openMenue()
    
def onSwitchZoomModw(sender):
    global zoom_mode
    zoom_mode = sender.value
    
    
def onButtonExit(_):
    saveAnnotation()
    global s
    sv.close()
    
def onButtonTest(_):
    pass

### ---------------------- ###
### |\   /|   /\   | |\  | ###
### | \ / |  /  \  | | \ | ###
### |  V  | /----\ | |  \| ###
### ---------------------- ###

@on_main_thread
def awake():
    global v
    global config
    initProgressLabel()
    initUIItems()
    initMenuView()
    v['touch_panel'].multitouch_enabled = True
    v['slider_zoom'].continuous = True
    v['Image'].content_mode = ui.CONTENT_SCALE_ASPECT_FIT
    v['Image'].background_color = 'white'
    v['curtain'].center = v['touch_panel'].center
    v['curtain'].bring_to_front()
    v['curtain'].touch_enabled = False
    v['guidBox'].border_color = config.theme_colors[0]['guide']
    
    global zoom_mode
    zoom_mode = v['menu_view']['menu']['switch_zoom_mode'].value

def start():
    global v
    global centerPos
    global initialImageScale
    
    centerPos = v['touch_panel'].center
    
    global imgOffset
    imgOffset = {
        'x': -v['Image'].x,
        'y': -v['Image'].y
    }
    initialImageScale = [v['touch_panel'].height, v['touch_panel'].width]
    createAncorGuide()
    
    v['guidBox'].center = centerPos
    
    initSlideBarView()
    initOverlaySystem()
    
    loadClassesFile()
    if not openLastEdetedFile():
        openPhotoBySelectPhoto()
    
    def a():
        v['curtain'].alpha = 0
    def b():
        v.remove_subview(v['curtain'])
    ui.animate(a, completion=b)
    
def main():
    global v
    global sv
    
    status_bar_height = 20
    
    v = ui.load_view()
    sv = ui.View(frame=v.bounds, name='superview')
    
    v.y = status_bar_height
    v.height -= status_bar_height
    v.flex = 'WH'
    sv.add_subview(v)
    awake()
            
    sv.present('fullscreen', hide_title_bar=True)
    start()

if __name__ == '__main__':
    main()

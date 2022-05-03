# -*- coding: utf-8 -*-

is_assets_reverse = False
is_large_blank = False

theme_colors = (
    {
        'box': (1,0,1),
        'boxbg': (0,0,0,0),
        'selectedbox': (1,0,1),
        'selectedboxbg': (1,1,1,0.4),
        'guide': (0,1,0)
    },
    {
        'box': (1,1,0),
        'boxbg': (0,0,0,0),
        'selectedbox': (1,1,0),
        'selectedboxbg': (0,0,0,0.2),
        'guide': (0,0,1)
    },
    {
        'box': (0,1,1),
        'boxbg': (0,0,0,0),
        'selectedbox': (0,1,1),
        'selectedboxbg': (1,1,1,0.4),
        'guide': (1,0,0)
    },
)

ancore_guid_names = [
    'ancorGuideTL',
    'ancorGuideTM',
    'ancorGuideTR',
    'ancorGuideML',
    'ancorGuideMR',
    'ancorGuideBL',
    'ancorGuideBM',
    'ancorGuideBR',
    'ancorGuideC',
    ]

class slideBarView():
    notthing = 0
    vertical = 1
    holizontal = 2
    
selected_border_width = 2
deselected_border_width = 1

# -*- coding: utf-8 -*-

import photos, dialogs
from compair_strings import compairString

def getSortedAlbums(albumAssetCollections):
    sorted = []
    for AAC in albumAssetCollections:
        for i, s in enumerate(sorted):
            if not compairString(AAC.title, s.title):
                sorted.insert(i, AAC)
                break
        else:
            sorted.append(AAC)
    return sorted

def getAlbumWithDialog():
    albumAssetCollections = photos.get_albums()
    albumAssetCollections = getSortedAlbums(albumAssetCollections)
    albumTitles = [a.title for a in albumAssetCollections]
    selectedAlbumTitle = dialogs.list_dialog(
        title='アルバムを選択',
        items=albumTitles
        )
    
    if selectedAlbumTitle == None:
        exit()
    else:
        selectedAlbumNum = albumTitles.index(selectedAlbumTitle)
        return albumAssetCollections[selectedAlbumNum]
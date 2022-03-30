# -*- coding: utf-8 -*-

import glob
import os

files = glob.glob('result/*')

print

if files:
    print('result内のすべてのファイルが削除されます。よろしいですか？')
    raw_input('> ')
    print('必要なファイルは退避させましたか？')
    raw_input('> ')
    print('本当によろしいですね？')
    raw_input('> ')
    for f in files:
        if not f.endswith('classes.txt'):
            os.remove(f)
    print('削除しました。')
else:
    print('ファイルはありませんでした。')

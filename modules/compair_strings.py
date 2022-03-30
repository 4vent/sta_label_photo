# -*- coding: utf-8 -*-

def compairString(large, small):
    for l, s in zip(large, small):
        if l == s:
            continue
        else:
            if ord(l) > ord(s):
                return True
            else:
                return False
# -*- coding: utf-8 -*-

import math

class Ease():
    @classmethod
    def liner(self, start, end, progress):
        trimd = min(1, max(0, progress))
        return (end - start) * trimd + start
    @classmethod
    def inSine(self, start, end, progress):
        trimd = min(1, max(0, progress))
        return (end - start) * (1 - math.cos(trimd * math.pi / 2)) + start
    @classmethod
    def inQuad(self, start, end, progress):
        trimd = min(1, max(0, progress))
        return (end - start) * (trimd ** 2) + start
    @classmethod
    def inQuad_inverse(self, start, end, value):
        progress = math.sqrt(max((value - start) / (end - start), 0))
        return progress
    @classmethod
    def InExpo(self, start, end, progress):
        trimd = min(1, max(0, progress))
        return  start if trimd == 0 else (end - start) * (pow(2, 10 * trimd - 10)) + start
        
if __name__ == '__main__':
    print('start')
    print(str(0.5))
    print(str(1/2))
    for i in range(20):
        num = int(100 * Ease.inSine(0.5, 0.0625, float(i)/20))
        print('=' * num + ' ' * (40-num))
    print('end')

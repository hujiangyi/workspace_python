#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# PreEqualizationParam
import pnmp.utils.PreEqualizationParamStringRead
class PreEqualizationParam:
    empty = False
    mtIndex = 0
    sybom = 0
    tapCount = 0
    taps = []
    def pause(self,mibData):
        #print mibData
        #print len(mibData)
        if '' == mibData :
            print 'empty'
            self.empty = True
            return
        mibData = mibData.replace(':','')
        preEqualizationParamStringRead = pnmp.utils.PreEqualizationParamStringRead.PreEqualizationParamStringRead()
        preEqualizationParamStringRead.init(mibData)
        self.mtIndex = preEqualizationParamStringRead.readNByteToNumber(1)
        self.sybom = preEqualizationParamStringRead.readNByteToNumber(1)
        self.tapCount = preEqualizationParamStringRead.readNByteToNumber(1)
        d = preEqualizationParamStringRead.readNByteToNumber(1)
        for i in range(0,8) :
            print i
            self.taps.append(complex(0,0))
        for i in range(8,self.tapCount + 8) :
            print i
            real = self.encode(preEqualizationParamStringRead.readNByteToNumber(2))
            imag = self.encode(preEqualizationParamStringRead.readNByteToNumber(2))
            self.taps.append(complex(real,imag))

    def encode(self,i):
        tmp = i & 0xF000
        if tmp==0x0 or tmp == 0xF000 :
            re = i & 0xFFF
            flag = i & 0x800
            if flag == 0x800 :
                re = ~i
                re = re & 0xFFF
                re = -1 * (re + 1)
            return re
        else :
            re = i
            flag = i & 0x8000
            if flag == 0x8000 :
                re = ~i
                re = re & 0xFFFF
                re = -1 * (re +1)
            return re
    def toArray(self):
        #print len(self.taps)
        return self.taps

    def isEmpty(self):
        return self.empty
    def setEmpty(self,b):
        self.empty = b
        self.empty = False
        self.mtIndex = 0
        self.sybom = 0
        self.tapCount = 0
        self.taps = []
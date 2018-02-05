#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# PreEqualizationParamStringRead

class PreEqualizationParamStringRead:
    str=''
    index=0
    BYTELENGTH=2
    def init(self,s):
        self.str=s

    def readNByteToNumber(self,n):
        re = 0
        for i in range(0,n) :
            b = self.readByte()
            ub = b & 0xFF
            m = ub << (8 * (n - i - 1))
            #print 'b=' + `b` + ';ub=' + `ub` + ';m='+ `m` + ';i='+ `i` + ';n=' + `n`
            re += m
        return re

    def readByte(self):
        #print 'index=' + `self.index`
        if '' == self.str :
            print 'NullPointerException'
            raise Exception('NullPointerException')
        if len(self.str) >= self.index + self.BYTELENGTH :
            nStr = self.str[self.index:self.index + self.BYTELENGTH]
            b = int(nStr,16)
            #print 'nStr:' + nStr + ';b=' + `b`
            self.index += self.BYTELENGTH
            return b
        else :
            print 'IndexOutOfBoundsException'
            raise Exception('IndexOutOfBoundsException')

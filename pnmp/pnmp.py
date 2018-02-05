#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# PNMP Example
from pnmp.utils import PnmpUtils as utils, PreEqualizationParam
import matplotlib.pyplot as pl
import numpy as np
import Color
macList = ['10:C6:1F:CD:C3:7A', '5C:C6:D0:62:D9:72', '80:B6:86:CC:1A:FC']

freqResult = np.fft.fftfreq(32);
freqShiftResult = np.fft.fftshift(freqResult);
colorArray = Color.colorArray(1)
mibData = '08011800ff00ff01fe03f97f07fd01ff00ff0000ff00ffff000000ff030310f0f0f0f0e1e8d7baafaca64b0ded000000000000000000000000000000000000f3f3e100000000000000000000000000000000000000020000000001000001010000000000'

pep = PreEqualizationParam.PreEqualizationParam()
pep.pause(mibData)
if not pep.isEmpty():
    print 'x1 *********************************'
    x1 = pep.toArray()
    mtc = utils.mtc(x1)
    mtr = utils.mtr(x1)
    amplitudes = utils.amplitudes(x1)
    amplitudes = utils.toArray24(amplitudes)
    print(amplitudes)
    freqResult = utils.freqResult(x1)
    #redLineValue = np.fft.fftshift(freqResult);
    #pl.plot(freqShiftResult, redLineValue, 'r')
    pl.bar(np.arange(24), amplitudes, color=colorArray[0])
else :
    print 'x1 error'

mibData2 = '08011800ff000000ff00fe7f01ff00ff00ff000000ff000000ff0000030310f0f0f0f0e1e8d7baafaca64b0ded000000000000000000000000000000000000f3f3e100000000000000000000000000000000000000020000000001000001010000000000'
pep2 = PreEqualizationParam.PreEqualizationParam()
pep2.setEmpty(False)
pep2.pause(mibData2)
if not pep2.isEmpty():
    print 'x2 *********************************'
    x2 = pep2.toArray()
    mtc = utils.mtc(x2)
    mtr = utils.mtr(x2)
    freqResult = utils.freqResult(x2)
    #greenLineValue = np.fft.fftshift(freqResult);
    #pl.plot(freqShiftResult,greenLineValue,'g')
else :
    print 'x2 error'
#pl.axis([-0.5,0.5,-3.5,3.5])
#pl.grid(True, color = "y")
pl.ylim(-100,0);
pl.show()
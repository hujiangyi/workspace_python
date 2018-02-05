#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# PnmpUtils
import numpy as np
import math
import cmath


def mte(taps):
    tap = taps[15]
    return abs(tap)


def preMTE(taps):
    re = 0
    for i in range(8, 15):
        tap = taps[i]
        re += abs(tap)
    return re


def postMTE(taps):
    re = 0
    for i in range(16, 32):
        tap = taps[i]
        re += abs(tap)
    return re


def tte(taps):
    re = 0
    # print len(taps)
    for i in range(8, 32):
        tap = taps[i]
        re += abs(tap)
    return re


def mtc(taps):
    _tte = tte(taps)
    _mte = mte(taps)
    if _mte != 0:
        return math.log10(_tte / _mte)
    else:
        raise Exception('mte can not be null')


def mtr(taps):
    _tte = tte(taps)
    _mte = mte(taps)
    if (_tte - _mte) != 0:
        return math.log10(_mte / (_tte - _mte))
    else:
        raise Exception('(_tte - _mte) can not be null')


def mrLevel(taps):
    _tte = tte(taps)
    _postMTE = postMTE(taps)
    if _tte != 0:
        return 10 * math.log(_postMTE / _tte)
    else:
        raise Exception('tte can not be null')


def nmtTER(taps):
    _tte = tte(taps)
    _mte = mte(taps)
    if _tte != 0:
        return 10 * math.log((_tte - _mte) / _tte)
    else:
        raise Exception('tte can not be null')


def preMTTER(taps):
    _preMTE = preMTE(taps)
    _tte = tte(taps)
    if _tte != 0:
        return 10 * math.log(_preMTE / _tte)
    else:
        raise Exception('tte can not be null')


def postMTTER(taps):
    _postMTE = postMTE(taps)
    _tte = tte(taps)
    if _tte != 0:
        return 10 * math.log(_postMTE / _tte)
    else:
        raise Exception('tte can not be null')


def ppesr(taps):
    _preMTE = preMTE(taps)
    _postMTE = postMTE(taps)
    if _postMTE != 0:
        return 10 * math.log(_preMTE / _postMTE)
    else:
        raise Exception('postMTE can not be null')


def tdr(taps, channelWidth):
    maxIndex = 0
    max = 0
    for i in range(0, len(taps)):
        tap = taps[i]
        te = abs(tap)
        if te > max:
            max = te
            maxIndex = i
    x1 = maxIndex
    y0 = abs(taps[maxIndex - 1])
    y1 = abs(taps[maxIndex])
    y2 = abs(taps[maxIndex + 1])
    a = (y0 - 2 * y1 + y2) / 2
    xm = (y0 - y2) / (4 * a)
    xOut = x1 + xm
    delayPerSymbol = 6.25;
    if channelWidth == 1600000:
        delayPerSymbol = 12.5
    elif channelWidth == 3200000:
        delayPerSymbol = 6.25
    elif (channelWidth == 6400000):
        delayPerSymbol = 3.125
    return (xOut - 8) * delayPerSymbol / 16 * 0.000001 * 299792458


def freqResult(taps):
    param = np.array(taps)
    squareP = np.square(param)
    sumP = np.sum(squareP)
    sqrtP = cmath.sqrt(sumP)
    dividesP = param / sqrtP
    fftP = np.fft.fft(dividesP)
    logP = 20 * np.log10(abs(fftP))
    return logP


def amplitudes(taps):
    param = np.array(taps)
    _tte = tte(taps)
    logP = 20 * np.log10(abs(param) / _tte)
    return logP


def toArray24(taps):
    re = []
    for i, v in enumerate(taps):
        if i >= 8:
            re.append(v)
    return re

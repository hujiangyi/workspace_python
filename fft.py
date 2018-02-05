#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# PNMP Example

import matplotlib.pyplot as pl
import numpy as np

np.arr

def fftResult(param,n) :
	result = np.fft.fft(param);

	realResult = np.real(result);
	imagResult = np.imag(result);
	sRealResult = np.square(realResult);
	sImagResult = np.square(imagResult);
	addResult = np.add(sRealResult,sImagResult);
	sqrtResult = np.sqrt(addResult);
	logResult = 10 * np.log(sqrtResult /n);
	return logResult;

freqResult = np.fft.fftfreq(32);
freqShiftResult = np.fft.fftshift(freqResult);

param1 = np.array([
    0 +0j,
    0 +0j,
    0 +0j,
    0 +0j,
    0 +0j,
    0 +0j,
    0 +0j,
    0 +0j,
    -1 +0j,
    0 +1j,
    -2 -3j,
    3 +4j,
    -6.0 -5.0j,
    8 +9j,
    -16 -22j,
    494 +0j,
    -17 -20j,
    56 -40j,
    85 -41j,
    -30 +3j,
    31 -27j,
    -4 -6j,
    1 -2j,
    1 -9j,
    -2 +2j,
    -1 -3j,
    -1 +0j,
    0 +0j,
    -1 +0j,
    0 +0j,
    0 +0j,
    0 +0j
]);

value1 = fftResult(param1,494);
redLineValue = np.fft.fftshift(value1);
pl.plot(freqShiftResult,redLineValue,'r')

param2 = np.array([
	0.0 +0.0j,
	0.0 +0.0j,
	0.0 +0.0j,
	0.0 +0.0j,
	0.0 +0.0j,
	0.0 +0.0j,
	0.0 +0.0j,
	0.0 +0.0j,
	0.0 -1.0j,
	-1.0 +1.0j,
	0.0 -2.0j,
	-1.0 +2.0j,
	1.0 -6.0j,
	-2.0 +10.0j,
	-2.0 -27.0j,
	510.0 +0.0j,
	-1.0 -29.0j,
	5.0 -11.0j,
	-2.0 +4.0j,
	-1.0 -3.0j,
	0.0 +2.0j,
	-1.0 -2.0j,
	-1.0 +2.0j,
	-1.0 -1.0j,
	0.0 +1.0j,
	0.0 -2.0j,
	0.0 +0.0j,
	-3.0 -1.0j,
	-1.0 -1.0j,
	-1.0 +0.0j,
	0.0 +1.0j,
	-1.0 +0.0j
]);
value2 = fftResult(param2,510);
greenLineValue = np.fft.fftshift(value2);

pl.plot(freqShiftResult,greenLineValue,'g')


pl.plot(freqShiftResult,yLineValue,'y')

pl.show()
#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# PNMP Example

import matplotlib.pyplot as pl
import numpy as np
import cmath

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
squareP1 = np.square(param1);
sumP1 = np.sum(squareP1);
sqrtP1 = cmath.sqrt(sumP1);
dividesP1 = param1 / sqrtP1;
fftP1 = np.fft.fft(dividesP1);
logP1 = 20 * np.log10(fftP1);
redLineValue = np.fft.fftshift(logP1);
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

squareP2 = np.square(param2);
sumP2 = np.sum(squareP2);
sqrtP2 = cmath.sqrt(sumP2);
dividesP2 = param2 / sqrtP2;
fftP2 = np.fft.fft(dividesP2);
logP2 = 20 * np.log10(fftP2);
greenLineValue = np.fft.fftshift(logP2);
pl.plot(freqShiftResult,greenLineValue,'g')
pl.axis([-0.5,0.5,-3.5,3.5])
pl.grid(True, color = "y") 
pl.show()
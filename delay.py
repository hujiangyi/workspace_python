#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# PNMP Example

import matplotlib.pyplot as pl
import numpy as np

param1 = np.array([
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
    -1 +0j
]);

param2 = np.array([
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
realResult = np.real(param1);
imagResult = np.imag(param1);
sRealResult = np.square(realResult);
sImagResult = np.square(imagResult);
addResult = np.add(sRealResult,sImagResult);
logResult = 10 * np.log(addResult /addResult[8]);

index = np.arange(param1.shape[0])
pl.plot(index,logResult,'r')
pl.show()

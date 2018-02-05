#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# PNMP utils

import matplotlib.pyplot as pl
import numpy as np

def fftResult(param) :
	result = np.fft.fft(param);

	realResult = np.real(result);
	imagResult = np.imag(result);
	sRealResult = np.square(realResult);
	sImagResult = np.square(imagResult);
	addResult = np.add(sRealResult,sImagResult);
	sqrtResult = np.sqrt(addResult);
	logResult = 10 * np.log(addResult /addResult[0]);
	return logResult;

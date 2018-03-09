import matplotlib.pyplot as pl
import numpy as np
import xlrd
import pickle
import Color
from pnmp.utils import PnmpUtils as utils

fig = pl.gcf()
fig.set_size_inches(10, 8)

freqResult = np.fft.fftfreq(32)
freqShiftResult = np.fft.fftshift(freqResult)

macList = ['10:C6:1F:CD:C3:7A', '5C:C6:D0:62:D9:72', '80:B6:86:CC:1A:FC']

excel = 'Classification.xls'
rb = xlrd.open_workbook(excel)
sheetR = rb.sheet_by_name('10.223.35.114_964886528_1')
nrows = sheetR.nrows
ncols = sheetR.ncols
colorArray = Color.colorArray(nrows)
ymax = 3.5
ymin = -3.5
figureCount = 1
pl.figure(figureCount)
for i in range(1, nrows):
    mac = sheetR.cell(i, 1).value
    freqResultData = sheetR.cell(i, 14).value
    freqResult = pickle.loads(freqResultData)
    for result in freqResult:
        if result > ymax:
            ymax = result
        if result < ymin:
            ymin = result
    lineValue = np.fft.fftshift(freqResult)
    if mac in macList or True:
        figureCount += 1
        pl.figure(figureCount)
        axFreq = pl.subplot(211)
        axAmplitudes = pl.subplot(212)
        amplitudesData = sheetR.cell(i, 15).value
        amplitudes = pickle.loads(amplitudesData)
        amplitudes = utils.toArray24(amplitudes)
        print amplitudes
        pl.figure(figureCount)
        pl.sca(axFreq)
        pl.axis([-0.5, 0.5, ymin, ymax])
        pl.grid(True, color="y")
        pl.plot(freqShiftResult, lineValue, colorArray[i], label=mac)
        pl.sca(axAmplitudes)
        barMin = 0
        for v in amplitudes:
            if barMin > v and v != -np.inf:
                barMin = v
        print np.isfinite(barMin)
        amplitudes = amplitudes - barMin
        pl.xlim(-1, 25)
        pl.bar(np.arange(24), amplitudes, color=colorArray[i], label=mac,bottom =barMin)

    pl.figure(1)
    pl.plot(freqShiftResult, lineValue, colorArray[i], label=mac)
pl.figure(1)
pl.legend(loc='upper center', shadow=True, fontsize='small')
pl.axis([-0.5, 0.5, ymin, ymax])
pl.grid(True, color="y")
pl.show()

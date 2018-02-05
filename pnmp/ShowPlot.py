import matplotlib.pyplot as pl
import numpy as np
import xlrd
from xlutils.copy import copy
import pickle
import Color

fig = pl.gcf()
fig.set_size_inches(10,8)

freqResult = np.fft.fftfreq(32)
freqShiftResult = np.fft.fftshift(freqResult)

excel = 'Classification_mtc.xls'
rb = xlrd.open_workbook(excel)
sheetR = rb.sheet_by_name('more1')
nrows = sheetR.nrows
ncols = sheetR.ncols
colorArray = Color.colorArray(nrows)
ymax = 3.5
ymin = -3.5
for i in range(1, nrows):
    mac = sheetR.cell(i, 1).value
    freqResultData = sheetR.cell(i, 14).value
    freqResult = pickle.loads(freqResultData)
    for result in freqResult:
        if result > ymax:
            ymax = result
        if result < ymin:
            ymin = result
    print freqResult
    lineValue = np.fft.fftshift(freqResult);
    pl.plot(freqShiftResult, lineValue, colorArray[i],label=mac)
#pl.legend(loc='upper center', shadow=True, fontsize='small')
pl.axis([-0.5, 0.5, ymin, ymax])
pl.grid(True, color="y")
pl.show()

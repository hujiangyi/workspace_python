import xlrd
import xlwt
from xlutils.copy import copy
from pnmp.utils import PnmpUtils as utils, PreEqualizationParam
import pickle

from Tkinter import *
from tkFileDialog import *
from tkMessageBox import *

root = Tk()
excelPath = StringVar()
imagePath = StringVar()
def selectOltExcelPath():
    path_ = askopenfilename()
    excelPath.set(path_)
def selectImagePath():
    path_ = askdirectory()
    imagePath.set(path_)
def closeDialog():
    if excelPath == None or excelPath.get() == '':
        showerror('error','The configuration file must be selected')
        return
    root.destroy()
    doCalc()

def getValue(globalValue,value):
    re = value
    if value == None or '' == value:
        re = globalValue
    return re
def doCalc():
    macList = []
    excel = excelPath.get()
    excelResult = 'Calculation.xls'
    rb = xlrd.open_workbook(excel)
    wb = xlwt.Workbook()
    sheetCount = len(rb.sheets())
    for si in range(sheetCount):
        print '%%%%%%%%%%%%%%%%%%%%%%%%%%' + `si` + '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        sheetName = `si`
        sheetR = rb.sheet_by_index(si)
        sheetW = wb.add_sheet('main')
        nrows = sheetR.nrows
        ncols = sheetR.ncols
        wi = 0
        sheetW.write(wi, 0, 'ip')
        sheetW.write(wi, 1, 'mac')
        sheetW.write(wi, 2, 'managerIp')
        sheetW.write(wi, 3, 'cmcIndex')
        sheetW.write(wi, 4, 'cmIndex')
        sheetW.write(wi, 5, 'equalizationData')
        sheetW.write(wi, 6, 'upChannelId')
        sheetW.write(wi, 7, 'upChannelFreq')
        sheetW.write(wi, 8, 'upChannelWidth')
        sheetW.write(wi, 9, 'upTxPower')
        sheetW.write(wi, 10, 'upRxPower')
        sheetW.write(wi, 11, 'upSignalNoise')
        sheetW.write(wi, 12, 'mtc')
        sheetW.write(wi, 13, 'mtr')
        sheetW.write(wi, 14, 'freqResult')
        sheetW.write(wi, 15, 'amplitudes')
        for i in range(1,nrows):
            mac = sheetR.cell(i,1).value
            equalizationData = sheetR.cell(i, 5).value
            if equalizationData == 'error':
                continue
            pep = PreEqualizationParam.PreEqualizationParam()
            pep.setEmpty(False)
            pep.pause(equalizationData)
            if not pep.isEmpty():
                taps = pep.toArray()
                try:
                    col = []
                    for j in range(0,ncols):
                        col.append(sheetR.cell(i,j).value)
                    wi += 1
                    mtc = utils.mtc(taps)
                    mtr = utils.mtr(taps)
                    freqResult = utils.freqResult(taps)
                    freqResultData = pickle.dumps(freqResult)
                    amplitudes = utils.amplitudes(taps)
                    if mac in macList:
                        print amplitudes
                    amplitudesData = pickle.dumps(amplitudes)
                    for i,v in enumerate(col):
                        sheetW.write(wi, i, v)
                    sheetW.write(wi, 12, mtc)
                    sheetW.write(wi, 13, mtr)
                    sheetW.write(wi, 14, freqResultData)
                    sheetW.write(wi,15, amplitudesData)
                except BaseException, msg:
                    print mac + ' error ' + `msg`
            else:
                print mac + ' error'
        wb.save(excelResult)
    wb.save(excelResult)


Label(root,text='excel').grid(row=0,column=0)
Entry(root, textvariable=excelPath).grid(row=0, column=1)
Button(root,text='select',command=selectOltExcelPath).grid(row=0,column=2)
Button(root,text='complte',command=closeDialog).grid(row=2,column=1)
root.mainloop()
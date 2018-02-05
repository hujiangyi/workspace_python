import xlrd
from xlutils.copy import copy
from pnmp.utils import PnmpUtils as utils, PreEqualizationParam
import pickle

macList = ['10:C6:1F:CD:C3:7A', '5C:C6:D0:62:D9:72', '80:B6:86:CC:1A:FC']
excel = 'CM.xls'
rb = xlrd.open_workbook(excel)
wb = copy(rb)
sheetCount = len(rb.sheets())
for si in range(sheetCount):
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%' + `si` + '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    sheetName = `si`
    sheetR = rb.sheet_by_index(si)
    sheetW = wb.get_sheet(si)
    nrows = sheetR.nrows
    ncols = sheetR.ncols
    wi = 0
    sheetW.write(wi, 12, 'mtc')
    sheetW.write(wi, 13, 'mtr')
    sheetW.write(wi, 14, 'freqResult')
    sheetW.write(wi, 15, 'amplitudes')
    wi += 1
    for i in range(1,nrows):
        mac = sheetR.cell(i,1).value
        equalizationData = sheetR.cell(i, 5).value
        pep = PreEqualizationParam.PreEqualizationParam()
        pep.setEmpty(False)
        pep.pause(equalizationData)
        if not pep.isEmpty():
            taps = pep.toArray()
            try:
                mtc = utils.mtc(taps)
                mtr = utils.mtr(taps)
                freqResult = utils.freqResult(taps)
                freqResultData = pickle.dumps(freqResult)
                amplitudes = utils.amplitudes(taps)
                if mac in macList:
                    print amplitudes
                amplitudesData = pickle.dumps(amplitudes)
                sheetW.write(wi, 12, mtc)
                sheetW.write(wi, 13, mtr)
                sheetW.write(wi, 14, freqResultData)
                sheetW.write(wi,15, amplitudesData)
            except BaseException, msg:
                print mac + ' error ' + `msg`
        else:
            print mac + ' error'
        wi += 1
    wb.save(excel)
wb.save(excel)
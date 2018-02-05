import xlrd
import xlwt

sheetWMap = {}
def createSheet(wb,sheetName):
    global sheetWMap
    sheetW = None
    if sheetWMap.has_key(sheetName) :
        sheetW = sheetWMap[sheetName]
    else :
        sheetW = wb.add_sheet(sheetName)
        sheetWMap[sheetName] = sheetW
        sheetW.write(0, 0, 'ip')
        sheetW.write(0, 1, 'mac')
        sheetW.write(0, 2, 'managerIp')
        sheetW.write(0, 3, 'cmcIndex')
        sheetW.write(0, 4, 'cmIndex')
        sheetW.write(0, 5, 'equalizationData')
        sheetW.write(0, 6, 'upChannelId')
        sheetW.write(0, 7, 'upChannelFreq')
        sheetW.write(0, 8, 'upChannelWidth')
        sheetW.write(0, 9, 'upTxPower')
        sheetW.write(0, 10, 'upRxPower')
        sheetW.write(0, 11, 'upSignalNoise')
        sheetW.write(0, 12, 'mtc')
        sheetW.write(0, 13, 'mtr')
        sheetW.write(0, 14, 'freqResult')
        sheetW.write(0, 15, 'amplitudes')
    return sheetW

def insertRow(wb,sheetName,col):
    sheetW = createSheet(wb,sheetName)
    row = len(sheetW.get_rows())
    for i,v in enumerate(col):
        sheetW.write(row, i, v)

excel = 'CM.xls'
resultExcel = 'Classification_snr.xls'
rb = xlrd.open_workbook(excel)
wb = xlwt.Workbook()
sheetR = rb.sheet_by_index(0)
nrows = sheetR.nrows
ncols = sheetR.ncols
for i in range(1, nrows):
    col = []
    for j in range(0,ncols):
        col.append(sheetR.cell(i,j).value)
    snrStr = sheetR.cell(i, 11).value
    if snrStr == '' or snrStr == None or snrStr == 'error' :
        insertRow(wb, 'continue', col)
        continue
    snr = float(snrStr) / 10
    if snr > 50  :
        insertRow(wb,'more50',col)
    elif snr >= 40 and snr < 50 :
        insertRow(wb,'between40and50',col)
    elif snr >= 30 and snr < 40:
        insertRow(wb,'between30and40',col)
    elif snr < 30  and snr != 0:
        insertRow(wb,'less30',col)
    elif snr == 0 :
        insertRow(wb,'equal0',col)
wb.save(resultExcel)



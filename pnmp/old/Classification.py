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

def createSheetName(ip,cmcIndex,channelId):
    try:
        return ip + '_' + `int(cmcIndex)` + '_' + `int(channelId)`
    except :
        print ip
        print cmcIndex
        print channelId

excel = 'CMresult.xls'
resultExcel = 'Classification.xls'
rb = xlrd.open_workbook(excel)
wb = xlwt.Workbook()
sheetR = rb.sheet_by_index(0)
nrows = sheetR.nrows
ncols = sheetR.ncols
for i in range(1, nrows):
    col = []
    for j in range(0,ncols):
        col.append(sheetR.cell(i,j).value)
    managerIp = sheetR.cell(i, 2).value
    cmcIndex = sheetR.cell(i, 3).value
    upChannelId = sheetR.cell(i, 6).value
    if managerIp == '' or managerIp == None :
        continue
    if upChannelId == 'error' :
        continue
    sheetName = createSheetName(managerIp,cmcIndex,upChannelId)
    print sheetName
    sheetW = createSheet(wb,sheetName)
    row = len(sheetW.get_rows())
    print row
    for i,v in enumerate(col):
        sheetW.write(row, i, v)
wb.save(resultExcel)



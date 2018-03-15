import xlrd
import xlwt
import datetime

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
filterIp = ['10.223.35.10']
# filterIp = []
excel = 'Classification.xls'
resultExcel = 'Classification_filter_{}.xls'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
rb = xlrd.open_workbook(excel)
wb = xlwt.Workbook()
sheets = rb.sheets()
oltMtrResult = {}
for sheetR in sheets:
    nrows = sheetR.nrows
    ncols = sheetR.ncols
    for i in range(1, nrows):
        col = []
        for j in range(0,ncols):
            col.append(sheetR.cell(i,j).value)
        ip = sheetR.cell(i, 0).value
        managerIp = sheetR.cell(i, 2).value
        cmcIndex = sheetR.cell(i, 3).value
        upChannelId = sheetR.cell(i, 6).value
        mtc = sheetR.cell(i, 12).value
        #filter mtc more then 2dB
        if mtc != None and mtc != '' and mtc > 2 and managerIp in filterIp:
            if oltMtrResult.has_key(managerIp):
                cmcList = oltMtrResult[managerIp]
                if cmcList.has_key(cmcIndex) :
                    upChannelList = cmcList[cmcIndex]
                    if upChannelList.has_key(upChannelId):
                        cmList = upChannelList[upChannelId]
                    else :
                        cmList = []
                        upChannelList[upChannelId] = cmList
                else :
                    cmList = []
                    cmcList[cmcIndex] = {upChannelId:cmList}
            else:
                cmList = []
                oltMtrResult[managerIp] = {cmcIndex : {upChannelId : cmList}}
            cmList.append(col)
        #filter sheet page
        if managerIp == '' or managerIp == None or managerIp not in filterIp:
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

oltList = sorted(oltMtrResult)
for oltKey in oltList:
    cmcList = sorted(oltMtrResult[oltKey])
    for cmcKey in cmcList:
        upChannelList = sorted(oltMtrResult[oltKey][cmcKey])
        for upChannelKey in upChannelList :
            cmList = oltMtrResult[oltKey][cmcKey][upChannelKey]
            for col in cmList:
                sheetW = createSheet(wb, 'main')
                row = len(sheetW.get_rows())
                for i, v in enumerate(col):
                    sheetW.write(row, i, v)
wb.save(resultExcel)



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
        sheetW.write(0, 0, 'mac')
        sheetW.write(0, 1, 'managerIp')
        sheetW.write(0, 2, 'cmcIndex')
        sheetW.write(0, 3, 'oltname')
        sheetW.write(0, 4, 'ccmac')
        sheetW.write(0, 5, 'ccname')
    return sheetW

def createSheetName(ip,cmcIndex,channelId):
    try:
        return ip + '_' + `int(cmcIndex)` + '_' + `int(channelId)`
    except :
        print ip
        print cmcIndex
        print channelId
excel1 = 'cmc.xlsx'
excel2 = 'abc.xls'
resultExcel = 'result.xls'
rb = xlrd.open_workbook(excel1)
sheets = rb.sheets()
macs = []
for sheetR in sheets:
    nrows = sheetR.nrows
    ncols = sheetR.ncols
    for i in range(1, nrows):
        col = []
        for j in range(0,ncols):
            col.append(sheetR.cell(i,j).value)
        col[0] = col[0].replace(':','')
        macs.append(col)

rb2 = xlrd.open_workbook(excel2)
sheets2 = rb2.sheets()
oltMap = {}
for sheetR in sheets2:
    nrows = sheetR.nrows
    ncols = sheetR.ncols

    for i in range(1, nrows):
        oltIp = sheetR.cell(i, 0).value
        cmcIndex = sheetR.cell(i, 1).value
        oltname = sheetR.cell(i, 2).value
        cmcMac = sheetR.cell(i, 3).value
        cmcName = sheetR.cell(i, 4).value
        cmcMap = {}
        if oltMap.has_key(oltIp):
            cmcMap = oltMap[oltIp]
        else :
            oltMap[oltIp] = cmcMap
        cmcMap[cmcIndex] = {
            'oltName':oltname,
            'cmcMac':cmcMac,
            'cmcName':cmcName
        }

wb = xlwt.Workbook()
for row,mac in enumerate(macs):
    cmcMap = oltMap[mac[1]]
    cmc = cmcMap[mac[2]]
    sheetW = createSheet(wb,'main')
    sheetW.write(row + 1, 0, mac[0])
    sheetW.write(row + 1, 1, mac[1])
    sheetW.write(row + 1, 2, mac[2])
    sheetW.write(row + 1, 3, cmc['oltName'])
    sheetW.write(row + 1, 4, cmc['cmcMac'])
    sheetW.write(row + 1, 5, cmc['cmcName'])
wb.save(resultExcel)



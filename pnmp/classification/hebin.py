import xlrd
import xlwt
import datetime

from pnmp.classification.BaseClassification import BaseClassification


class hebin(BaseClassification) :
    def __init__(self):
        path = 'mas/'
        self.oltExcel = '{}abc.xls'.format(path)
        self.macs = []
        self.oltMap = {}
        BaseClassification.__init__(self,'{}cmc.xlsx'.format(path),'{}hebin.xls'.format(path))
        self.makeRule()
    def doClassification(self,wb,rowCount,colName,colValue):
        colName.append('oltname')
        colName.append('cmcmac')
        colName.append('cmcname')
        if self.oltMap.has_key(colValue[2]) :
            cmcMap = self.oltMap[colValue[2]]
            if cmcMap.has_key(colValue[3]) :
                cmc = cmcMap[colValue[3]]
                if cmc is not None :
                    colValue.append(cmc['oltName'])
                    colValue.append(cmc['cmcMac'])
                    colValue.append(cmc['cmcName'])
                    self.insertRow(wb,'main',colName,colValue)

    def makeRule(self):
        rb = xlrd.open_workbook(self.oltExcel)
        sheets = rb.sheets()
        for sheetR in sheets:
            nrows = sheetR.nrows
            ncols = sheetR.ncols

            for i in range(1, nrows):
                oltIp = sheetR.cell(i, 0).value
                cmcIndex = sheetR.cell(i, 1).value
                oltname = sheetR.cell(i, 2).value
                cmcMac = sheetR.cell(i, 3).value
                cmcName = sheetR.cell(i, 4).value
                cmcMap = {}
                if self.oltMap.has_key(oltIp):
                    cmcMap = self.oltMap[oltIp]
                else:
                    self.oltMap[oltIp] = cmcMap
                cmcMap[cmcIndex] = {
                    'oltName': oltname,
                    'cmcMac': cmcMac,
                    'cmcName': cmcName
                }


if __name__ == '__main__' :
    bc =hebin()
    bc.excelParser()

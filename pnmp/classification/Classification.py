import xlrd
import xlwt

class BaseClassification:
    def __init__(self, srcFile, disFile,sheetIndex = 0):
        self.srcFile = srcFile
        self.disFile = disFile
        self.sheetIndex = sheetIndex
        self.sheetMap = {}
    def excelParser(self):
        colName = []
        rb = xlrd.open_workbook(self.srcFile)
        wb = xlwt.Workbook()
        sheetR = self.rb.sheet_by_index(self.sheetIndex)
        nrows = sheetR.nrows
        ncols = sheetR.ncols
        for i in range(0,ncols) :
            colName.append(sheetR.cell(0, i).value)
        for i in range(1, nrows):
            colValue = []
            for j in range(0, ncols):
                colValue.append(sheetR.cell(i, j).value)
            self.doClassification(self,wb,i,colName,colValue)
        wb.save(self.disFile)
    def insertRow(self,wb,sheetName,colName,colValue):
        sheetW = self.createSheet(wb, sheetName,colName)
        row = len(sheetW.get_rows())
        for i, v in enumerate(colValue):
            sheetW.write(row, i, v)
    def createSheet(self,wb,sheetName,colName):
        sheetW = None
        if self.sheetMap.has_key(sheetName):
            sheetW = self.sheetMap[sheetName]
        else:
            sheetW = wb.add_sheet(sheetName)
            self.sheetMap[sheetName] = sheetW
            for i, v in enumerate(colName):
                sheetW.write(0,i,v)
        return sheetW
    def doClassification(self,wb,rowCount,colName,colValue):
        self.insertRow(wb,'sheetName',colName,colValue)
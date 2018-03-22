from pnmp.classification.BaseClassification import BaseClassification


class WHFilterSpaceRow(BaseClassification) :
    def __init__(self):
        BaseClassification.__init__(self,'CMresult.xls','WHFilterSpaceRow.xls')
    def doClassification(self,wb,rowCount,colName,colValue):
        if colValue[5] != '':
            self.insertRow(wb,'sheetName',colName,colValue)

if __name__ == '__main__' :
    bc =WHFilterSpaceRow()
    bc.excelParser()
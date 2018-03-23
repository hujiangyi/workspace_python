from BaseClassification import BaseClassification

class FilterSpaceRow(BaseClassification) :
    def __init__(self):
        path = 'mas/'
        BaseClassification.__init__(self,'{}CMresult.xls'.format(path),'{}FilterSpaceRow.xls'.format(path))
    def doClassification(self,wb,rowCount,colName,colValue):
        if colValue[5] != '' and  colValue[5] != 'error':
            self.insertRow(wb,'sheetName',colName,colValue)

if __name__ == '__main__' :
    bc =FilterSpaceRow()
    bc.excelParser()
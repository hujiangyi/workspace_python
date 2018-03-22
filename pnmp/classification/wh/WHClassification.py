from pnmp.classification.BaseClassification import BaseClassification

import datetime

class WHClassification(BaseClassification) :
    def __init__(self):
        self.filterIp = []
        self.oltMtrResult = {}
        self.sheetWMap = {}
        self.colName = [ 'ip','mac','managerIp','cmcIndex','cmIndex','equalizationData','upChannelId','upChannelFreq','upChannelWidth','upTxPower','upRxPower','upSignalNoise','mtc','mtr','freqResult','amplitudes']
        excel = 'Calculation.xls'
        resultExcel = 'Classification_filter_{}.xls'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        BaseClassification.__init__(self,excel,resultExcel)

    def createSheetName(self,ip, cmcIndex, channelId):
        try:
            return ip + '_' + `int(cmcIndex)` + '_' + `int(channelId)`
        except:
            print ip
            print cmcIndex
            print channelId
    def doClassification(self,wb,rowCount,colName,colValue):
        ip = colValue[0]
        managerIp = colValue[2]
        cmcIndex = colValue[3]
        upChannelId = colValue[6]
        mtc = colValue[12]
        #filter mtc more then 2dB
        if mtc != None and mtc != '' and mtc > 2 and (len(self.filterIp) == 0 or managerIp in self.filterIp):
            if self.oltMtrResult.has_key(managerIp):
                cmcList = self.oltMtrResult[managerIp]
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
                self.oltMtrResult[managerIp] = {cmcIndex : {upChannelId : cmList}}
            cmList.append(colValue)
        #filter sheet page
        if managerIp == '' or managerIp == None or (len(self.filterIp) !=0 and managerIp not in self.filterIp):
            return
        if upChannelId == 'error' :
            return
        sheetName = self.createSheetName(managerIp,cmcIndex,upChannelId)
        print sheetName
        self.insertRow(wb,sheetName,self.colName,colValue)
    def doAfterSave(self,wb):
        oltList = sorted(self.oltMtrResult)
        for oltKey in oltList:
            cmcList = sorted(self.oltMtrResult[oltKey])
            for cmcKey in cmcList:
                upChannelList = sorted(self.oltMtrResult[oltKey][cmcKey])
                for upChannelKey in upChannelList:
                    cmList = self.oltMtrResult[oltKey][cmcKey][upChannelKey]
                    for col in cmList:
                        self.insertRow(wb, 'main',self.colName,col)

if __name__ == '__main__' :
    bc =WHClassification()
    bc.excelParser()
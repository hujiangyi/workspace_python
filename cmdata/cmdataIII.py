import xlrd
import xlwt
import time

from CollectThreadIII import CollectThreadIII

class CmDataIII:
    def __init__(self):
        self.wb=xlwt.Workbook()
        self.wi = 0
        self.sheetW = self.wb.add_sheet('result')
        self.sheetW.write(self.wi, 0, 'ip')
        self.sheetW.write(self.wi, 1, 'mac')
        self.sheetW.write(self.wi, 2, 'managerIp')
        self.sheetW.write(self.wi, 3, 'cmcIndex')
        self.sheetW.write(self.wi, 4, 'cmIndex')
        self.sheetW.write(self.wi, 5, 'equalizationData')
        self.sheetW.write(self.wi, 6, 'upChannelId')
        self.sheetW.write(self.wi, 7, 'upChannelFreq')
        self.sheetW.write(self.wi, 8, 'upChannelWidth')
        self.sheetW.write(self.wi, 9, 'upTxPower')
        self.sheetW.write(self.wi, 10, 'upRxPower')
        self.sheetW.write(self.wi, 11, 'upSignalNoise')
    def writeResult(self,ip,mac,managerIp,cmcIndex,cmIndex,equalizationData,upChannelId,upChannelFreq,upChannelWidth,upTxPower,upRxPower,upSignalNoise):
        self.wi = self.wi + 1
        self.sheetW.write(self.wi, 0, ip)
        self.sheetW.write(self.wi, 1, mac)
        self.sheetW.write(self.wi, 2, managerIp)
        self.sheetW.write(self.wi, 3, cmcIndex)
        self.sheetW.write(self.wi, 4, cmIndex)
        self.sheetW.write(self.wi, 5, equalizationData)
        self.sheetW.write(self.wi, 6, upChannelId)
        self.sheetW.write(self.wi, 7, upChannelFreq)
        self.sheetW.write(self.wi, 8, upChannelWidth)
        self.sheetW.write(self.wi, 9, upTxPower)
        self.sheetW.write(self.wi, 10, upRxPower)
        self.sheetW.write(self.wi, 11, upSignalNoise)
        print '{} {} {} {}'.format(self.wi,ip,mac,managerIp)

    def doCollect(self) :
        excel='CM.xls'
        resultExcel='CMresult.xls'
        rb = xlrd.open_workbook(excel)
        sheetCount=len(rb.sheets())
        count = 0
        oltCmList = {}
        for si in range(sheetCount) :
            print '%%%%%%%%%%%%%%%%%%%%%%%%%%' + `si` + '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
            sheetName = `si`
            sheetR=rb.sheet_by_index(si)
            nrows = sheetR.nrows
            ncols=sheetR.ncols
            for i in range(nrows) :
                ip=sheetR.cell(i,3).value
                if ip!='' and ip != '0.0.0.0' and 'cmIp' not in ip:
                    count = count + 1
                    mac=sheetR.cell(i,2).value
                    managerIp=sheetR.cell(i,0).value
                    managerCommunity=sheetR.cell(i,1).value
                    cmcIndex=sheetR.cell(i,4).value
                    cmIndex=sheetR.cell(i,5).value
                    if oltCmList.has_key(managerIp):
                        cmList = oltCmList[managerIp]
                    else :
                        cmList = []
                        oltCmList[managerIp] = cmList
                    cmList.append({
                        'ip':ip,
                        'mac':mac,
                        'managerIp':managerIp,
                        'managerCommunity':managerCommunity,
                        'cmcIndex':cmcIndex,
                        'cmIndex':cmIndex
                    })

        threads = []
        for managerIp,cmList in oltCmList.items():
            collectThreadIII = CollectThreadIII(self,cmList,managerIp)
            collectThreadIII.setDaemon(True)
            collectThreadIII.start()
            threads.append(collectThreadIII)
        while True:
            if len(threads) == 0:
                break
            removeThread = []
            for t in threads:
                if not t.isAlive():
                    removeThread.append(t)
            for t in removeThread:
                print 'end thread:{}'.format(t.oltIp)
                threads.remove(t)
        self.wb.save(resultExcel)

CmDataIII().doCollect()
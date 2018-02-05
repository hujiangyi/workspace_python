import traceback

from UpgradeOlt import UpgradeOlt

class UpgradeCcmts(UpgradeOlt):
    def run(self):
        row={"identifyKey":"ip",
             "ip":self.host,
             "result":"start",
             "isAAA":self.isAAA == '1',
             "userName":self.userName,
             "password":self.password,
             "enablePassword":self.enablePassword}
        self.listView.insertRow(row)
        self.doTelnet()
        self.doUpgrade()
    def doUpgrade(self):
        try:
            self.mduUpgrade(self.vlan,self.gateway,self.ftpServer,self.ftpUserName,self.ftpPassword,self.imageFileName)
            self.checkAllUpgradeStatus()
            self.clearConfig(self.vlan)
            self.writeResult('cmts count[' + `len(self.allCmts)` + '] success[' + `self.successCount` + '] faild[' + `self.faildCount` + ']' )
        except BaseException, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
    def doCollectData(self):
        try:
            self.collectData('after')
        except BaseException, msg:
            self.log(`msg`)
            print 'traceback.format_exc():\n%s' % traceback.format_exc()

    def connect(self,host,isAAA,userName,password,enablePassword,cmip,mask,cmgateway,logPath,sheetW,excelRow,vlan,gateway,ftpServer,ftpUserName,ftpPassword,imageFileName,listView):
        print 'connect to host ' + host
        self.listView = listView
        self.vlan = vlan
        self.gateway = gateway
        self.ftpServer = ftpServer
        self.ftpUserName = ftpUserName
        self.ftpPassword = ftpPassword
        self.imageFileName = imageFileName
        self.initCmIpArg(cmip,mask,cmgateway)
        self.initListView(listView)
        self.initExcel(sheetW,excelRow)
        self.initLog(logPath,host)
        self.setTelnetArg(host,isAAA,userName,password,enablePassword)



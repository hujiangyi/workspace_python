import traceback
import time
from UpgradeOlt import UpgradeOlt
from ConfigCcmtsIp import ConfigCcmtsIp


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
            state = self.mduUpgrade(self.vlan,self.gateway,self.ftpServer,self.ftpUserName,self.ftpPassword,self.imageFileName)
            if state:
                self.checkAllUpgradeStatus()
                self.doResetCmts()
                self.clearConfig(self.vlan)
                self.writeResult('cmts count[' + `len(self.allCmts)` + '] success[' + `self.successCount` + '] faild[' + `self.faildCount` + ']' )
            else :
                self.clearConfig(self.vlan)
                self.writeResult('no cmts upgraded')
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

    def connect(self,host,isAAA,userName,password,enablePassword,cmip,mask,cmgateway,logPath,sheetW,excelRow,vlan,gateway,ftpServer,ftpUserName,ftpPassword,imageFileName,threadNum,version,listView):
        print 'connect to host ' + host
        self.listView = listView
        self.vlan = vlan
        self.gateway = gateway
        self.ftpServer = ftpServer
        self.ftpUserName = ftpUserName
        self.ftpPassword = ftpPassword
        self.imageFileName = imageFileName
        self.threadNum = threadNum
        self.version = version
        self.initCmIpArg(cmip,mask,cmgateway)
        self.initListView(listView)
        self.initExcel(sheetW,excelRow)
        self.initLog(logPath,host)
        self.setTelnetArg(host,isAAA,userName,password,enablePassword)

    def mduUpgrade(self,vlan,gateway,ftpServer,ftpUsername,ftpPassword,imageFileName):
        self.log('mduUpgrade')
        self.allCmts,self.allkey,self.allVersion = self.getAllOnlineCmts(raiseException=True)
        self.successCount = 0
        self.faildCount = 0
        state,msg = self.confgVlan(vlan,gateway)
        upgradeCmts = []
        if state :
            upgradeThreads = []
            for slot,portMap in self.allCmts.items():
                for port,deviceList in portMap.items():
                    state,msg = self.doConfigPon(vlan,slot,port)
                    if state :
                        for device in deviceList:
                            key = '{}/{}/{}'.format(slot,port,device)
                            nversion = self.allVersion[key]
                            if nversion != None and nversion != 'no version' and nversion != '' and nversion != self.version:
                                upgradeCmts.append(key)
                                while True:
                                    for t in upgradeThreads:
                                        if not t.isAlive():
                                            state,msg = t.getUpgradeResult()
                                            if not state :
                                                self.log(msg)
                                                #self.writeResult(msg)
                                                self.faildCount = self.faildCount + 1
                                            else :
                                                self.successCount = self.successCount + 1
                                            upgradeThreads.remove(t)
                                            break
                                    if len(upgradeThreads) < self.threadNum :
                                        configCcmtsIp = ConfigCcmtsIp()
                                        configCcmtsIp.connect(self,self.host, self.isAAA, self.userName, self.password, self.enablePassword, self.cmip, self.mask,
                                                             self.cmgateway, vlan, gateway,
                                                             ftpServer,slot,port,device)
                                        configCcmtsIp.setDaemon(True)
                                        configCcmtsIp.start()
                                        upgradeThreads.append(configCcmtsIp)
                                        break
                                    else :
                                        time.sleep(10)
                            else :
                                row = {"identifyKey": "ip",
                                       "ip": slot + '/' + port + '/' + device,
                                       "result": "start",
                                       "isAAA": self.isAAA == '1',
                                       "userName": self.userName,
                                       "password": self.password,
                                       "enablePassword": self.enablePassword}
                                self.listView.insertChildRow(self.host,row)
                                self.listView.setData('{}_{}'.format(self.host, key), 'result', nversion)
                    else :
                        self.log(msg)
                        #self.writeResult(msg)

            while True:
                if len(upgradeThreads) == 0:
                    break
                removeThread = []
                for t in upgradeThreads:
                    if not t.isAlive():
                        state, msg = t.getUpgradeResult()
                        if not state:
                            self.log(msg)
                            # self.writeResult(msg)
                            self.faildCount = self.faildCount + 1
                        else:
                            self.successCount = self.successCount + 1
                        removeThread.append(t)
                        break
                for t in removeThread:
                    upgradeThreads.remove(t)
        else :
            self.log(msg)
            #self.writeResult(msg)
        if len(upgradeCmts) > 0:
            self.send('end')
            self.readuntil('#')
            self.send('configure terminal')
            self.readuntil('(config)#')
            self.send('upgrade mdu image ftp ' + ftpServer + ' ' + ftpUsername + ' ' + ftpPassword + ' ' + imageFileName)
            self.readuntil('Upgrade software image of all mdu device? (y/n) [n]')
            self.send('y')
            self.readuntil('(config)#')
            return True
        else :
            return False


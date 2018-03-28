import traceback
import time
from UpgradeOlt import UpgradeOlt
from ConfigCcmtsIp import ConfigCcmtsIp
from ResetCcmts import ResetCcmts


class UpgradeCcmts(UpgradeOlt):
    def run(self):
        row={"identifyKey":"ip",
             "ip":self.host,
             "result":"start",
             "clearResult":"",
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
                self.writeResult('cmts count[' + `len(self.allkey)` + '] success[' + `self.successCount` + '] faild[' + `self.faildCount` + ']' )
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

    def connect(self,host,isAAA,userName,password,enablePassword,cmip,mask,cmgateway,logPath,sheetW,excelRow,vlan,gateway,ftpServer,ftpUserName,ftpPassword,imageFileName,threadNum,version,cmvlan,listView):
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
        self.cmvlan = cmvlan
        self.initCmIpArg(cmip,mask,cmgateway)
        self.initListView(listView)
        self.initExcel(sheetW,excelRow)
        self.initLog(logPath,host)
        self.setTelnetArg(host,isAAA,userName,password,enablePassword)

    def mduUpgrade(self,vlan,gateway,ftpServer,ftpUsername,ftpPassword,imageFileName):
        self.log('mduUpgrade')
        self.allCmts,self.allkey,self.allVersion,self.allMac = self.getAllOnlineCmts(raiseException=True)
        self.successCount = 0
        self.faildCount = 0
        boards = self.allBoard()
        slotType = {}
        for board in boards:
            slotId = board[0]
            if '*' in slotId:
                slotId = slotId[0:len(slotId) - 1]
            slotType[slotId] = board[2]
        # state,msg = self.confgVlan(vlan,gateway)
        upgradeCmts = []
        # if state :
        upgradeThreads = []
        for slot,portMap in self.allCmts.items():
            for port,deviceList in portMap.items():
                slotVlan = int(vlan)
                slotGateway = int(gateway)
                state,msg = self.doConfigPon(slotVlan,self.cmvlan,slot,port,slotType['{}'.format(slot)],slotGateway)
                if state :
                    for device in deviceList:
                        key = '{}/{}/{}'.format(slot,port,device)
                        nversion = self.allVersion[key]
                        mac = self.allMac[key]
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
                                                         self.cmgateway, slotVlan, slotGateway,
                                                         ftpServer,slot,port,device,slotType['{}'.format(slot)],self.cmvlan,self.logPath,mac)
                                    configCcmtsIp.setDaemon(True)
                                    configCcmtsIp.start()
                                    upgradeThreads.append(configCcmtsIp)
                                    time.sleep(1)
                                    break
                                else :
                                    time.sleep(10)
                        else :
                            row = {"identifyKey": "ip",
                                   "ip": slot + '/' + port + '/' + device,
                                   "result": "start",
                                   "clearResult": "",
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
        # else :
        #     self.log(msg)
            #self.writeResult(msg)
        if len(upgradeCmts) > 0:
            self.send('end')
            self.readuntil('#')
            self.send('configure terminal')
            self.readuntil('(config)#')
            # self.send('upgrade mdu image ftp ' + ftpServer + ' ' + ftpUsername + ' ' + ftpPassword + ' ' + imageFileName)
            # self.readuntil('Upgrade software image of all mdu device? (y/n) [n]')
            # self.send('y')
            # self.readuntil('(config)#')
            return True
        else :
            return False


    ####################################################CC upgrade######################################################
    def confgVlan(self,vlan,gateway):
        self.log('makeVlan {} gateway {}.254.0.1'.format(vlan,gateway))
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('vlan {}'.format(vlan))
        self.readuntil('(config-vlan-{})#'.format(vlan))
        self.send('vlan-interface ip-address {}.254.0.1 255.0.0.0'.format(gateway))
        re = self.readuntil('(config-vlan-{})#'.format(vlan))
        if '%' in re and '%Entry exists' not in re:
            return False,re
        else:
            return True,''

    def doConfigPon(self,vlan,cmvlan,slot,port,slotType,gateway):
        self.log('configPon vlan {} cm vlan{} key{}/{}'.format(vlan,cmvlan,slot,port))
        self.confgVlan(vlan,gateway)
        time.sleep(2)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        cmds = ['interface pon {}/{}'.format(slot,port),'interface gpon {}/{}'.format(slot,port)]
        cmd,re = self.checkCmd(cmds,errorMessage= 'interface number error.')
        if cmd != None:
            if not self.isGpon(slotType):
                if cmvlan == 1:
                    cmvlan = 0
            if cmvlan != 0:
                self.send('vlan batch {} transparent'.format(vlan))
                self.readuntil('{}/{})#'.format(slot,port))
                self.send('vlan batch {} transparent'.format(cmvlan))
            else :
                self.send('vlan batch {} transparent'.format(vlan))
            re = self.readuntil('{}/{})#'.format(slot,port))
            if '%' in re:
                return False,re
            else:
                return True,''
        else :
            return False,re

    def getCcmtsVersion(self,key):
        cmd = 'show ccmts version | include C{}\\b'.format(key)
        self.send(cmd)
        re = self.readuntil('#')
        lines = re.split('\r\n')
        for line in lines:
            if '' == line.strip():
                continue
            if 'show ccmts version' in line:
                continue
            if 'Filtering...' in line:
                continue
            if '#' in line:
                continue
            cols = line.split()
            return cols[2]
        return 'no version'

    def getAllOnlineCmts(self,raiseException=False):
        allCmts = {}
        allVersion = {}
        allMac = {}
        allKey = []
        self.log('getAllOnlineCmts')
        self.send('end')
        self.readuntil('#')
        self.send('show ccmts | include online.*\\bCC8800.*E\\b')
        re = self.readuntil('#')
        lines = re.split('\r\n')
        for line in lines:
            if '' == line.strip():
                continue
            if 'show ccmts' in line:
                continue
            if 'Filtering...' in line:
                continue
            if '#' in line:
                continue
            cols = line.split()
            nums = cols[0].strip().split('/')
            slot = nums[0][1:len(nums[0])]
            port = nums[1]
            device = nums[2]
            mac = cols[1]
            key = '{}/{}/{}'.format(slot,port,device)
            if not allKey.__contains__(key) :
                allKey.append(key)
            version = self.getCcmtsVersion(key)
            self.log('{}:{}'.format(key,version))
            allVersion[key] = version
            allMac[key] = mac
            #print slot,port,device
            portMap = {}
            if allCmts.has_key(slot):
                portMap = allCmts[slot]
            else :
                allCmts[slot] = portMap
            deviceList = []
            if portMap.has_key(port) :
                deviceList = portMap[port]
            else :
                portMap[port] = deviceList
            deviceList.append(device)
        if len(allCmts) == 0 :
            self.log('No CMTS is on the OLT.')
            if raiseException :
                raise Exception('No CMTS is on the OLT.')
        return allCmts,allKey,allVersion,allMac

    def checkCmtsUpgradeStatus(self,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('show mdu image-upgrade-status interface {}'.format(key))
        re = self.readuntil('(config)#')
        lines = re.split('\r\n')
        for line in lines:
            if '' == line.strip():
                continue
            if 'show mdu image-upgrade-status interface' in line:
                continue
            if 'Filtering...' in line:
                continue
            if '#' in line:
                continue
            if 'Download image failed.'in line:
                return  False,True,line
            if 'Progress   :'in line:
                if '%' not in line:
                    return False,True,line
                else :
                    if '100%' in line:
                        return True,True,line
                    else :
                        return False,False,line
        return False,False,''
    def checkAllUpgradeStatus(self):
        self.log('checkAllUpgradeStatus')
        allKey = []
        upgradeStatus = {}
        upgradeStatusTimeout = {}
        while True:
            for slot,portMap in self.allCmts.items():
                for port,deviceList in portMap.items():
                    for device in deviceList:
                        key =  '{}/{}/{}'.format(slot,port,device)
                        nversion = self.allVersion[key]
                        if nversion != None and nversion != 'no version' and nversion != '' and nversion != self.version:
                            if not allKey.__contains__(key) :
                                allKey.append(key)
                            if not upgradeStatus.has_key(key) :
                                state,finish,result = self.checkCmtsUpgradeStatus(slot,port,device)
                                if state:
                                    upgradeStatus[key] = state
                                    self.log('{} upgrade state :{}:{}'.format(key,state,result),cmts=key)
                                else :
                                    if finish:
                                        upgradeStatus[key] = state
                                        self.log('{} upgrade state :{}:{}'.format(key,state,result),cmts=key)
                                    else :
                                        if not upgradeStatusTimeout.has_key(key) :
                                            upgradeStatusTimeout[key] = {
                                                'line' : result,
                                                'checktime' : int(time.time())
                                            }
                                        else :
                                            o = upgradeStatusTimeout[key]
                                            if o['line'] == result:
                                                if int(time.time()) - o['checktime'] > 60 :
                                                    upgradeStatus[key] = state
                                                    self.log('{} upgrade state :{}:{}'.format(key,state,result),cmts=key)
                                            else :
                                                o['checktime'] = int(time.time())
                                                upgradeStatusTimeout[key] = o
                                        self.log('{} upgrade not finish{}'.format(key,result),cmts=key)
            self.log('allKey:{};upgradeStatus{}'.format(len(allKey),len(upgradeStatus)))
            if len(allKey) == len(upgradeStatus):
                self.upgradeStatus = upgradeStatus
                return
            time.sleep(30)



    def doClearOnuIp(self,vlan,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        self.log('doClearOnuIp vlan {} {}/{}/{}'.format(vlan,slot,port,device),cmts=key,headName='clearResult')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface ccmts {}'.format(key))
        self.readuntil('(config-if-ccmts-{})#'.format(key))
        self.send('no onu-ipconfig cvlan ' + vlan)
        re = self.readuntil('(config-if-ccmts-' + slot + '/' + port + '/' + device + ')#')
        if '%' in re:
            self.log('doClearOnuIp error.',cmts=slot + '/' + port + '/' + device,headName='clearResult')
            return False,re
        else:
            self.log('doClearOnuIp success.',cmts=slot + '/' + port + '/' + device,headName='clearResult')
            return True,''

    def doClearPonVlanConfig(self,vlan,slot,port):
        self.log('doClearPonVlanConfig vlan {} {}/{}'.format(vlan,slot,port),headName='clearResult')
        self.doClearVlanConfig(vlan)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface pon {}/{}'.format(slot,port))
        self.readuntil('(config-if-pon-{}/{})#'.format(slot,port))
        self.send('no vlan batch {} transparent'.format(vlan))
        re = self.readuntil('(config-if-pon-{}/{})#'.format(slot,port))
        if '%' in re:
            return False,re
        else:
            return True,''

    def doClearVlanConfig(self,vlan):
        self.log('doClearVlanConfig vlan {}'.format(vlan),headName='clearResult')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('vlan {}'.format(vlan))
        self.readuntil('(config-vlan-{})#'.format(vlan))
        self.send('no vlan-interface')
        re = self.readuntil('(config-vlan-{})#'.format(vlan))
        if '%' in re:
            return False,re
        else:
            return True,''

    def resetCmts(self):
        self.log('reset all Cmts')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        resetCmts = []
        resetThreads = []
        for slot, portMap in self.allCmts.items():
            for port, deviceList in portMap.items():
                slotGateway = int(self.gateway) + int(slot)
                for device in deviceList:
                    key = '{}/{}/{}'.format(slot,port,device)
                    if self.upgradeStatus[key] :
                        nversion = self.allVersion[key]
                        mac = self.allMac[key]
                        if nversion != None and nversion != 'no version' and nversion != '' and nversion != self.version:
                            resetCmts.append(key)
                            while True:
                                for t in resetThreads:
                                    if not t.isAlive():
                                        state, msg = t.getResetResult()
                                        if not state:
                                            self.log(msg)
                                            # self.writeResult(msg)
                                            self.faildCount = self.faildCount + 1
                                        else:
                                            self.successCount = self.successCount + 1
                                        resetThreads.remove(t)
                                        break
                                if len(resetThreads) < self.threadNum / 2:
                                    resetCcmts = ResetCcmts()
                                    resetCcmts.connect(self, self.host, self.isAAA, self.userName, self.password,
                                                          self.enablePassword, slotGateway, slot, port, device,  self.logPath, mac)
                                    resetCcmts.setDaemon(True)
                                    resetCcmts.start()
                                    resetThreads.append(resetCcmts)
                                    time.sleep(1)
                                    break
                                else:
                                    time.sleep(10)

        while True:
            if len(resetThreads) == 0:
                break
            removeThread = []
            for t in resetThreads:
                if not t.isAlive():
                    state, msg = t.getResetResult()
                    if not state:
                        self.log(msg)
                        # self.writeResult(msg)
                        self.faildCount = self.faildCount + 1
                    else:
                        self.successCount = self.successCount + 1
                    removeThread.append(t)
                    break
            for t in removeThread:
                resetThreads.remove(t)

    def clearConfig(self,vlan):
        self.log('clearConfig',headName='clearResult')
        for slot,portMap in self.allCmts.items():
            for port,deviceList in portMap.items():
                slotVlan = int(vlan)
                #for device in deviceList:
                    #state,msg = self.doClearOnuIp(vlan,slot,port,device)
                    #if not state :
                    #    self.writeResult(msg)
                state,msg = self.doClearPonVlanConfig(slotVlan,slot,port)
                if not state :
                    self.writeResult(msg)
    def doResetCmts(self):
        self.log('doResetCmts',headName='clearResult')
        bArray,bKeys,allVersion,allMac = self.getAllOnlineCmts()
        self.log('online cmts count(' + `len(bKeys)` + ')')
        self.resetCmts()
        while True:
            nbArray,nbKeys,allVersion,allMac = self.getAllOnlineCmts()
            self.log('online cmts count before reset(' + `len(bKeys)` + ') after reset(' + `len(nbKeys)` + ')')
            if len(bKeys) == len(nbKeys) :
                for key,version in allVersion.items():
                    if self.upgradeStatus[key]:
                        self.listView.setData('{}_{}'.format(self.host,key), 'result', version)
                break
            time.sleep(30)



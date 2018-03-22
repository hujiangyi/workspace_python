import traceback
import time

from UpgradeOlt import *

class ConfigCcmtsIp(UpgradeOlt):
    def run(self):
        self.initLog(self.logPath,self.host)
        self.doTelnet()
        self.doConfig()
        self.close()
    def initLog(self,logPath,host):
        key = '{}_{}_{}'.format(self.slot,self.port,self.device)
        self.logPath = logPath
        self.cmdResultFile = open("{}{}_{}CmdResult.log".format(logPath,host,key), "w")
        self.logResultFile = open("{}{}_{}logFile.log".format(logPath,host,key), "w")
    def doConfig(self):
        try:
            self.state,self.msg = self.doConfigCcmts(self.vlan,self.gateway,self.ftpServer,self.slot,self.port,self.device)
        except BaseException, msg:
            self.state, self.msg = False,msg
            self.parent.log('traceback.format_exc():\n%s' % traceback.format_exc())
            print 'traceback.format_exc():\n%s' % traceback.format_exc()

    def connect(self,parent,host,isAAA,userName,password,enablePassword,cmip,mask,cmgateway,vlan,gateway,ftpServer,slot,port,device,slotType,cmvlan,logPath,mac):
        print 'connect to host ' + host
        self.parent = parent
        self.vlan = vlan
        self.gateway = gateway
        self.ftpServer = ftpServer
        self.slot = slot
        self.port = port
        self.device = device
        self.slotType = slotType
        self.cmvlan = cmvlan
        self.mac = mac
        self.initCmIpArg(cmip,mask,cmgateway)
        self.setTelnetArg(host,isAAA,userName,password,enablePassword)
        self.logPath = logPath

    def getUpgradeResult(self):
        return self.state,self.msg



    def doConfigCcmts(self,vlan,gateway,ftpServer,slot,port,device):
        row = {"identifyKey": "ip",
               "ip": slot + '/' + port + '/' + device,
               "result": "start",
               "clearResult": "",
               "isAAA": self.isAAA == '1',
               "userName": self.userName,
               "password": self.password,
               "enablePassword": self.enablePassword}
        self.parent.listView.insertChildRow(self.host,row)
        self.parent.log('configCcmts vlan '+ vlan + ' ' + slot + '/' + port + '/' + device,cmts=slot + '/' + port + '/' + device)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface ccmts ' + slot + '/' + port + '/' + device)
        self.readuntil('(config-if-ccmts-' + slot + '/' + port + '/' + device + ')#')
        self.send('onu-ipconfig ip-address ' + gateway + '.' + slot + '.' + port + '.' + device +  ' mask 255.0.0.0 gateway ' + gateway + '.254.0.1 cvlan ' + vlan)
        re = self.readuntil('(config-if-ccmts-' + slot + '/' + port + '/' + device + ')#')
        if '%This command does not support GPON CCMTS, and the corresponding GPON' in re:
            self.send('exit')
            self.readuntil('(config)#')
            self.send('interface gpon {}/{}'.format(slot,port))
            self.readuntil('(config-if-gpon-{}/{})#'.format(slot,port))
            self.send('onu-ipconfig {3} ip-index 1 static ip-address {0}.{1}.{2}.{3} mask 255.0.0.0 gateway {0}.254.0.1 vlan {4}'.format(gateway,slot,port,device,vlan))
            self.readuntil('(config-if-gpon-{}/{})#'.format(slot,port))
        time.sleep(5)
        self.send('telnet ' + gateway + '.' + slot + '.' + port + '.' + device)
        re = self.readuntilMutl(['Username:','username:','%Telnet exit successful','%Error:Connect to {}.{}.{}.{} timeout!'.format(gateway,slot,port,device),'%Connect to ' + gateway + '.' + slot + '.' + port + '.' + device + ' timeout!'])
        if '%Telnet exit successful' in re:
            self.parent.log('%Telnet exit successful',cmts=slot + '/' + port + '/' + device)
            return False,'%Telnet exit successful'
        elif '%Connect to ' + gateway + '.' + slot + '.' + port + '.' + device + ' timeout!' in re or '%Error:Connect to {}.{}.{}.{} timeout!'.format(gateway,slot,port,device) in re:
            self.parent.log('%Connect to ' + gateway + '.' + slot + '.' + port + '.' + device + ' timeout!',cmts=slot + '/' + port + '/' + device)
            return False,'%Connect to ' + gateway + '.' + slot + '.' + port + '.' + device + ' timeout!'
        self.send('admin')
        self.send('admin')
        self.send('enable')
        re = self.readuntilII('#')
        cmIp = None
        if not self.useNetRange :
            self.send('show cable modem | include online')
            re = self.readuntil('#')
            lines = re.split('\r\n')
            if len(lines) > 1  and "online" in lines[1]:
                cols = lines[1].split()
                cmIp = cols[1]
                self.cmgateway = None
                self.parent.log('cmts ip is ' + cmIp, cmts=slot + '/' + port + '/' + device)
                state,msg = self.configCmtsIp(cmIp, ftpServer,slot,port,device)
            else:
                self.parent.log('cmts does not specify.', cmts=slot + '/' + port + '/' + device)
                return False, 'cmts does not specify.'
        else :
            cmIp = self.parent.nextIp()
            while True:
                if cmIp == self.cmgateway :
                    cmIp = self.parent.nextIp()
                r = ping(cmIp)
                if r.ret_code == 0 :
                    cmIp = self.parent.nextIp()
                    if cmIp == self.cmgateway:
                        cmIp = self.parent.nextIp()
                else:
                    break
            self.parent.log('cmts ip is ' + cmIp, cmts=slot + '/' + port + '/' + device)
            state,msg = self.configCmtsIp(cmIp,ftpServer,slot,port,device)
            while not state:
                cmIp = self.parent.nextIp()
                if cmIp == self.cmgateway :
                    cmIp = self.parent.nextIp()
                state, msg = self.configCmtsIp(cmIp, ftpServer,slot,port,device)
        self.send('exit')
        self.readuntil('>')
        self.send('exit')
        self.send('')
        self.readuntil('#')
        return state,msg


    def configCmtsIp(self,cmIp,ftpServer,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface ccmts 1/1/1')
        self.readuntil('(config-if-ccmts-1/1/1)#')
        self.send('cable upstream 1-4 shutdown')
        self.readuntil('(config-if-ccmts-1/1/1)#')
        self.send('cable downstream 1-16 shutdown')
        self.readuntil('(config-if-ccmts-1/1/1)#')
        self.send('exit')
        self.readuntil('(config)#')
        self.send('no ip address primary')
        self.readuntil('(config)#')
        self.send('no ip address dhcp-alloc')
        self.readuntil('(config)#')
        if not self.isGpon(self.slotType) :
            if self.cmvlan == 1:
                self.cmvlan = 0
        if self.cmvlan != 0:
            self.send('interface vlanif {}'.format(self.cmvlan))
            self.readuntil('#')
            self.send('ip address ' + cmIp + ' ' + self.mask + ' primary')
            self.readuntil('#')
            self.send('exit')
            self.readuntil('#')
        else :
            self.send('ip address ' + cmIp + ' ' + self.mask + ' primary')
            self.readuntil('#')
        if self.cmgateway != None:
            self.send('gateway ' + self.cmgateway + '')
            self.readuntil('(config)#')
        self.send('super')
        self.readuntilII('Password:')
        self.send('8ik,(OL>')
        self.readuntil('(config-super)#')
        self.send('shell')
        self.readuntil('#')
        self.send('ping ' + ftpServer)
        self.readuntil('#')
        self.send('echo $?')
        re = self.readuntil('#')
        self.send('exit')
        self.readuntil('#')
        self.send('exit')
        self.readuntil('#')
        self.send('exit')
        self.readuntil('#')
        lines = re.split('\r\n')
        for s in lines:
            if 'echo $?' in s:
                continue
            if '#' in s:
                continue
            if '0' == s:
                self.parent.log('{}config success!cmIp:{}'.format(key,cmIp), cmts=slot + '/' + port + '/' + device)
                return True, ''
            else:
                self.parent.log('{}ftp server can not connect.cmIp:{}'.format(key,cmIp), cmts=slot + '/' + port + '/' + device)
                return False, '{}ftp server can not connect.cmIp:{}'.format(key,cmIp)

    def cmdLog(self, str):
        self.parent.cmdLog(str)
        try:
            self.cmdResultFile.write(str)
            self.cmdResultFile.flush()
        except BaseException, msg:
            print msg

    def log(self, str,cmts=None,headName='result'):
        self.parent.log(str,cmts,headName)
        try:
            str = datetime.datetime.now().strftime('%Y%m%d%H%M%S\t') + str + '\n'
            self.logResultFile.write(str)
            self.logResultFile.flush()
        except BaseException, msg:
            print msg
    def writeResult(self, msg,cmts=None):
        self.parent.writeResult(msg,cmts)


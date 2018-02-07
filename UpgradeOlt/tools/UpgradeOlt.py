from threading import *
from telnetlib import *
from IPy import *
from pyping import *
import time
import datetime
import os
import traceback

class UpgradeOlt(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.step = 1
    def doStep(self,step,func,args=None):
        if self.step < step :
            if args != None:
                func(*args)
            else :
                func()
            self.step = step
    def setRetryThreadR(self,retryThread):
        self.retryThread = retryThread
    def addRetry(self,args,step=None):
        arg = {}
        arg['args'] = args
        arg['step'] = step
        self.retryThread.retryList.append(arg)

    #################################################init###############################################################
    def doTelnet(self):
        try:
            self.telnet = Telnet(self.host)
        except BaseException, msg:
            print msg
            msg = 'host is unreachable!'
            self.writeResult(msg)
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
    def reconnect(self):
        self.close()
        self.log('reconnect telnet')
        self.doTelnet()
        self.send('')
        self.readuntil('#')

    def setTelnetArg(self, host, isAAA, userName, password, enablePassword):
        self.host = host
        self.isAAA = isAAA
        self.userName = userName
        self.password = password
        self.enablePassword = enablePassword
        self.log(self.host + ' ' + self.isAAA + '' + self.userName + '' + self.password + '' + self.enablePassword)
    def setAppPath(self,appPath):
        self.appPath = appPath

    def initCmIpArg(self,cmip,mask,cmgateway):
        self.cmip = cmip
        self.mask = mask
        self.cmgateway = cmgateway
        if self.cmip == None or self.cmip == '':
            self.useNetRange = False
        else :
            self.useNetRange = True
            self.ips = IP(self.cmip + '/' + self.mask)
            self.ipsIndex = 0
            self.ipsIndexLock = Lock()
    def nextIp(self):
        self.ipsIndexLock.acquire()
        try:
            self.ipsIndex = self.ipsIndex + 1
            return self.ips[self.ipsIndex].strCompressed()
        finally:
            self.ipsIndexLock.release()
    def initLog(self,logPath,host):
        self.logPath = logPath
        self.cmdResultFile = open(logPath + host + "CmdResult.log", "w")
        self.logResultFile = open(logPath + host + "logFile.log", "w")

    def initListView(self,listView):
        self.listView = listView
    def initExcel(self,sheetW,excelRow):
        self.sheetW = sheetW
        self.excelRow = excelRow

    ###############################################com##################################################################
    def close(self):
        try:
            self.log('close telnet ')
            self.telnet.close()
        except Exception, msg:
            self.log(`msg`)
            msg = 'telnet close failed'
            raise Exception(msg)

    def send(self, cmd):
        terminator = '\r'
        cmd = str(cmd)
        cmd += terminator
        try:
            msg = cmd
            self.telnet.write(cmd)
        except Exception, msg:
            self.log(`msg`)
            raise Exception("telnet write error!")

    def sendII(self, cmd):
        cmd = str(cmd)
        try:
            msg = cmd
            self.telnet.write(cmd)
        except Exception, msg:
            self.log(`msg`)
            raise Exception("telnet write error!")

    def read(self, delay=1):
        str = self.telnet.read_very_eager()
        self.cmdLog(str)
        return str

    def readuntil(self, waitstr='xxx', timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                tmp += self.read()
                time.sleep(1)
                if tmp.endswith('--More--'):
                    self.sendII(' ')
                if waitstr in tmp:
                    return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                tmp += self.read()
                #self.log(tmp)
                if self.needLogin(tmp):
                    tmp = ''
                    self.send('')
                    tmp += self.read()
                if waitstr in tmp:
                    return tmp

    def readuntilMutl(self, waitstrs=['xxx'], timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                time.sleep(1)
                tmp += self.read()
                if tmp.endswith('--More--'):
                    self.sendII(' ')
                for waitstr in waitstrs:
                    if waitstr in tmp:
                        return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                tmp += self.read()
                #self.log(tmp)
                if self.needLogin(tmp):
                    tmp = ''
                    self.send('')
                    tmp += self.read()
                for waitstr in waitstrs:
                    if waitstr in tmp:
                        return tmp

    def readuntilII(self, waitstr='xxx', timeout=0):
        tmp = ""
        if timeout != 0:
            delay = 0.0
            while delay <= timeout:
                time.sleep(1)
                tmp += self.read()
                if waitstr in tmp:
                    return tmp
                delay += 1
            raise Exception("wait str timeout")
        else:
            while True:
                tmp += self.read()
                if waitstr in tmp:
                    return tmp

    def needLogin(self, str):
        try:
            if 'assword:' in str:
                #self.log('CLI timeout need login.')
                if self.isAAA == '1':
                    self.send('')
                    re = self.readuntilII(waitstr='sername:', timeout=30)
                    self.send(self.userName)
                    self.readuntilII(waitstr='assword:', timeout=30)
                    self.send(self.password)
                    self.readuntilII('>', timeout=30)
                    self.send('en')
                    self.readuntilII('#', timeout=30)
                else:
                    self.send('')
                    self.readuntilII(waitstr='assword:', timeout=30)
                    self.send(self.password)
                    self.readuntilII('>', timeout=30)
                    self.send('en')
                    self.readuntilII('Enable Password:', timeout=30)
                    self.send(self.enablePassword)
                    self.readuntilII('#', timeout=30)
                return True
            else :
                return False
        except Exception, msg:
            self.log(`msg`)
            raise Exception("login faild!")

    def sleepT(self, delay):
        time.sleep(delay)
    def getMainBoardTypes(self):
        return ['mpu', 'mpub', 'meu', 'mef', 'mgu']

    def checkCmd(self,cmds):
        for cmd in cmds:
            self.send(cmd)
            re = self.readuntil('#')
            if '% Unknown command.' not in re:
                return cmd,re

    def cmdExists(self,checkCmd,default):
        runCmd = 'list | include ' + checkCmd
        self.send(runCmd)
        listresult = self.readuntil('#')
        lss = listresult.split('\r\n')
        cmd = default
        for s in lss:
            if runCmd in s:
                continue
            if checkCmd in s:
                cmd = checkCmd
        return cmd

    def cmdLog(self, str):
        self.cmdResultFile.write(str)
        self.cmdResultFile.flush()

    def log(self, str,cmts=None,headName='result'):
        print self.host,str
        str = datetime.datetime.now().strftime('%Y%m%d%H%M%S\t') + str + '\n'
        self.logResultFile.write(str)
        self.logResultFile.flush()
        if cmts == None:
            self.listView.setData(self.host,headName,str)
        else :
            self.listView.setData(self.host + "_" + cmts,headName,str)

    def writeResult(self, msg,cmts=None):
        if cmts == None:
            self.listView.setData(self.host,'result',msg)
        else :
            self.listView.setData(self.host + "_" + cmts,'result',msg)
        self.sheetW.write(self.excelRow, 5, msg)

    ###############################################download#############################################################
    def downloadImage(self):
        return False
    def allBoard(self):
        self.send('show board | include IS')
        re = self.readuntil('#')
        bs = re.split('\r\n')
        bArray = []
        for s in bs :
            if 'show board' in s:
                continue
            if 'Filtering...' in s:
                continue
            if '#' in s:
                continue
            if s == '':
                continue
            cols = s.split()
            if cols[4] == 'IS':
                bArray.append(cols)
        return bArray
    def rebootOlt(self):
        self.log('rebootOlt start ')
        self.send('end')
        self.readuntil('#')
        bArray = self.allBoard()
        self.log('online board count(' + `len(bArray)` + ')')
        self.send('system reboot ')
        re = self.readuntilMutl(['System will reboot! Continue?(y/n) [n]','#'])
        self.send('y')
        self.readuntil('System now is rebooting,please wait.')
        self.close()
        time.sleep(180)
        while True:
            r = ping(self.host)
            if r.ret_code == 0 :
                break
        time.sleep(180)
        self.doTelnet()
        self.send('')
        self.readuntil('#')
        while True:
            nbArray = self.allBoard()
            self.log('new online board count(' + `len(nbArray)` + ')')
            if len(bArray) == len(nbArray) :
                compare = True
                for i in range(0,len(nbArray)):
                    b = bArray[i]
                    nb = nbArray[i]
                    for j in range(0,len(nb)):
                        bCol = b[j]
                        nbCol = nb[j]
                        if bCol != nbCol :
                            self.log('compare False:' + `bArray` + ' ' + `nbArray`)
                            compare = False
                            break
                    else :
                        continue
                    break
                if compare :
                    break
        self.log('rebootOlt success ')

    def flashType(self):
        flashType = 0  # only tffs0 = 0 ;include tffs0 and yaffs2 = 1
        self.send('end')
        self.readuntil('#')
        self.send('cd /')
        self.readuntil('#')
        self.send('ls')
        lsInfo = self.readuntil('#')
        lis = lsInfo.split('\r\n')
        for s in lis:
            if 'yaffs2' in s:
                flashType = 1
        return flashType


    def freeSize(self,path):
        self.send('cd ' + path)
        pwdStr = self.readuntil('#')
        self.send('ls')
        lsInfo = self.readuntil('#')
        lis = lsInfo.split('\r\n')
        for s in lis:
            if 'Free size' in s:
                indexStart = s.index(':')
                indexEnd = s.index('bytes')
                ts = s[indexStart + 1:indexEnd].strip()
                return int(ts)

    def imageTypeAndFreeSize(self):
        self.log('imageTypeAndFreeSize')
        flashType = self.flashType()
        if flashType == 0 :
            tffs0FreeSize = self.freeSize('/tffs0')
            return flashType,tffs0FreeSize,0
        elif flashType == 1:
            tffs0FreeSize = self.freeSize('/tffs0')
            yaffs2FreeSize = self.freeSize('/yaffs2')
            return flashType,tffs0FreeSize,yaffs2FreeSize
        else:
            raise Exception("unkown image type")

    def imageFileSizeOnOlt(self,isActiveAndStandby,mainFile,otherFiles):
        self.log('imageFileSizeOnOlt')
        fileSizes = {}
        self.send('end')
        self.readuntil('#')
        cmds = ['show image-info all','show all file-info']
        if isActiveAndStandby :
            cmds = ['show image-info master all','show master all file-info']
        cmd,lsInfo = self.checkCmd(cmds)
        lis = lsInfo.split('\r\n')
        for s in lis:
            if cmd in s:
                continue
            elif 'Main mpu' in s:
                continue
            elif 'File Name' in s:
                continue
            elif '---' in s:
                continue
            elif 'Total size:' in s:
                continue
            elif '#' in s:
                continue
            cols = s.split()
            for f in otherFiles:
                if f in s:
                    fileSizes[f] = int(cols[3])
                    break
        return fileSizes

    def imageFileSize(self,mainFile,otherFiles):
        fileSizes = {}
        if not self.appPath.endswith('/'):
            self.appPath += '/'
        for f in otherFiles:
            try:
                fFileSize = os.path.getsize(self.appPath + f + '.bin')
                fileSizes[f] = int(fFileSize)
            except Exception, msg:
                self.log(`msg`)
        return fileSizes

    def checkFreeSize(self,isActiveAndStandby,mainFile,otherFiles):
        self.log('checkFreeSize')
        imageType,tffs0FreeSize,yaffs2FreeSize = self.imageTypeAndFreeSize()
        self.log('imageTypeAndFreeSize:' + `imageType` + '\t' + `tffs0FreeSize` + '\t' + `yaffs2FreeSize`)
        fileSizesOnOlt = self.imageFileSizeOnOlt(isActiveAndStandby,mainFile,otherFiles)
        self.log('imageFileSizeOnOlt:' + `fileSizesOnOlt`)
        fileSizes = self.imageFileSize(mainFile,otherFiles)
        self.log('imageFileSize:' + `fileSizes`)
        if imageType == 0:
            freeSize = 0
            freeSize +=  tffs0FreeSize
            for f in otherFiles:
                if fileSizesOnOlt.has_key(f):
                    freeSize +=  fileSizesOnOlt[f]
            needSize = 0
            for f in otherFiles:
                if fileSizes.has_key(f):
                    needSize += fileSizes[f]
            if needSize >= freeSize:
                raise Exception("checkFreeSize error")
        elif imageType == 1:
            freeSize = 0
            freeSize +=  yaffs2FreeSize
            for f in otherFiles:
                if fileSizesOnOlt.has_key(f):
                    freeSize +=  fileSizesOnOlt[f]
            needSize = 0
            for f in otherFiles:
                if fileSizes.has_key(f):
                    needSize += fileSizes[f]
            if needSize >= freeSize:
                raise Exception("checkFreeSize error")

    def allImageTypeAndFileName(self):
        self.send('end')
        self.readuntil('#')
        self.send('show system')
        systemInfo = self.readuntil(waitstr='#')
        si = systemInfo.split('\r\n')
        sysObjectId = ''
        for s in si:
            if 'System total service slots' in s:
                indexStart = s.index(':')
                indexEnd = len(s)
                if indexStart == -1:
                    raise Exception('Read olt type error')
                ts = s[indexStart + 1:indexEnd].strip()
                totalSlot = int(ts)
                # self.log('totalSlot:' + str(totalSlot))
                if totalSlot == 3:
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.2'
                elif totalSlot == 8:
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.3'
                elif totalSlot == 18:
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.1'
                else:
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.2.x'
        self.send('show board')
        boardInfo = self.readuntil(waitstr='#')
        # self.log(boardInfo)
        self.send('configure terminal')
        self.readuntil('(config)#')
        bs = boardInfo.split('\r\n')
        for s in bs:
            if 'show board' in s:
                continue
            if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s:
                continue
            if '------' in s:
                continue
            if 'Total:' in s:
                continue
            if '#' in s:
                continue
            slotid = s[2:4].strip()
            assignType = s[9:13].strip()
            presentType = s[26:33].strip()
            adminStatus = s[43:46]
            operationStatus = s[60:64]
            # self.log(slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus)
            if '*' in slotid:
                #self.log('slotid:' + slotid)
                if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.1':
                    #8601
                    if assignType == 'mpub':
                        return True,'mpub',['epu','geu','gpu','xgu','bootrom','bootrom-e500']
                    else:
                        return True,'mpu',['epu','geu','gpu','xgu','bootrom','bootrom-e500']
                if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.2':
                    #8602
                    return False,'mpu',['epu','geu','gpu','xgu','bootrom','bootrom-e500']
                elif sysObjectId == '1.3.6.1.4.1.32285.11.2.1.3':
                    #8603
                    if assignType == 'mpub':
                        return True,'mpub',['epu','geu','gpu','xgu','bootrom','bootrom-e500']
                    else:
                        return True,'mpu',['epu','geu','gpu','xgu','bootrom','bootrom-e500']
                else:
                    if 'meu' in assignType:
                        return False,'meu',['bootrom-e500']
                    elif 'mef' in assignType:
                        return False,'mef',['bootrom']
                    else:
                        return False,'mgu',['bootrom-e500']
    #################################################syncFile###########################################################
    def syncFile(self):
        self.sleepT(3)
        cmd = self.cmdExists('show file-sync-status','show file sync-status')
        self.log('sync config file')
        self.send('sync config file')
        re = self.readuntilMutl(['Are you sure?(y/n) [n]','#'])
        if '%' not in re:
            self.send('y')
            self.readuntil('#')
            self.send(cmd)
            tmp = self.read()
            while 'successfully' not in tmp:
                self.sleepT(10)
                self.send(cmd)
                tmp += self.read()
            self.log('sync app file')
            self.send('sync app file')
            self.readuntil('Are you sure?(y/n) [n]')
            self.send('y')
            self.readuntil('#')
            self.send(cmd)
            tmp = self.read()
            while 'successfully' not in tmp:
                self.sleepT(10)
                self.send(cmd)
                tmp += self.read()
            self.sleepT(3)
            self.writeResult('syncFile success')
        else:
            self.log('syncFile error:' + re)
            self.writeResult('syncFile error' + re)

    ###################################################upgrade##########################################################
    def upgradeAllBootrom(self):
        try:
            self.send('end')
            self.readuntil('#')
            self.send('show board')
            boardInfo = self.readuntil(waitstr='#')
            bis = boardInfo.split('\r\n')
            for bs in bis:
                if 'show board' in bs:
                    continue
                if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in bs:
                    continue
                if '------' in bs:
                    continue
                if 'Total:' in bs:
                    continue
                if '#' in bs:
                    continue
                # self.log(bs)
                slotid = bs[2:4].strip()
                assignType = bs[9:13].strip()
                presentType = bs[26:33].strip()
                adminStatus = bs[43:46].strip()
                operationStatus = bs[60:64].strip()
                #self.log(slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus)
                if '*' in slotid:
                    slotid = slotid[0:1]
                if operationStatus == 'IS':
                    cmd = 'upgrade bootrom slot ' + slotid
                    self.log(cmd)
                    self.send(cmd)
                    upgraderesult = self.readuntil(waitstr='#')
                    self.log(upgraderesult)
                    while '%' in upgraderesult:
                        self.send(cmd)
                        upgraderesult = self.readuntil(waitstr='#')
                        self.log(upgraderesult)
            self.writeResult('syncFile success')
            return True
        except Exception, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            return False
    def upgradeMpubBootrom(self):
        try:
            self.send('end')
            self.readuntil('#')
            self.send('show board')
            boardInfo = self.readuntil(waitstr='#')
            bis = boardInfo.split('\r\n')
            for bs in bis:
                if 'show board' in bs:
                    continue
                if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in bs:
                    continue
                if '------' in bs:
                    continue
                if 'Total:' in bs:
                    continue
                if '#' in bs:
                    continue
                # self.log(bs)
                slotid = bs[2:4].strip()
                assignType = bs[9:13].strip()
                presentType = bs[26:33].strip()
                adminStatus = bs[43:46].strip()
                operationStatus = bs[60:64].strip()
                #self.log(slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus)
                if 'mpu' not in assignType:
                    continue
                else :
                    if '*' in slotid:
                        slotid = slotid[0:1]
                if operationStatus == 'IS':
                    cmd = 'upgrade bootrom slot ' + slotid
                    self.log(cmd)
                    self.send(cmd)
                    upgraderesult = self.readuntil(waitstr='#')
                    self.log(upgraderesult)
                    while '%' in upgraderesult:
                        self.send(cmd)
                        upgraderesult = self.readuntil(waitstr='#')
                        self.log(upgraderesult)
            self.writeResult('syncFile success')
            return True
        except Exception, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            return False
    def upgradeServiceBootrom(self):
        try:
            self.send('end')
            self.readuntil('#')
            self.send('show board')
            boardInfo = self.readuntil(waitstr='#')
            bis = boardInfo.split('\r\n')
            for bs in bis:
                if 'show board' in bs:
                    continue
                if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in bs:
                    continue
                if '------' in bs:
                    continue
                if 'Total:' in bs:
                    continue
                if '#' in bs:
                    continue
                # self.log(bs)
                slotid = bs[2:4].strip()
                assignType = bs[9:13].strip()
                presentType = bs[26:33].strip()
                adminStatus = bs[43:46].strip()
                operationStatus = bs[60:64].strip()
                #self.log(slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus)
                if 'mpu' in assignType:
                    continue
                if operationStatus == 'IS':
                    cmd = 'upgrade bootrom slot ' + slotid
                    self.log(cmd)
                    self.send(cmd)
                    upgraderesult = self.readuntil(waitstr='#')
                    self.log(upgraderesult)
                    while '%' in upgraderesult:
                        self.send(cmd)
                        upgraderesult = self.readuntil(waitstr='#')
                        self.log(upgraderesult)
            self.writeResult('syncFile success')
            return True
        except Exception, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            return False
    #####################################################collectData####################################################
    def collectData(self,type):
        fo = open(self.logPath + self.host + type + 'Upgrade.txt', "w")
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.log('show ccmts summary')
        self.send('show ccmts summary')
        tmp = self.readuntil('(config)#')
        fo.write(tmp + '\n')
        fo.write('split------------------------------------------\n')
        self.log('show board')
        self.send('show board')
        tmp = self.readuntil('(config)#')
        fo.write(tmp + '\n')
        fo.write('split------------------------------------------\n')
        self.log('show cable modem summary')
        self.send('show cable modem summary')
        tmp = self.readuntil('(config)#')
        fo.write(tmp + '\n')
        fo.write('split------------------------------------------\n')
        self.log('show running-config')
        self.send('show running-config')
        tmp = self.readuntil('(config)#')
        fo.write(tmp + '\n')
        fo.write('split------------------------------------------\n')
        fo.flush()
        fo.close()

    ####################################################CC upgrade######################################################
    def confgVlan(self,vlan,gateway):
        self.log('makeVlan ' + vlan + ' gateway ' + gateway + '.254.0.1')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('vlan ' + vlan)
        self.readuntil('(config-vlan-' + vlan + ')#')
        self.send('vlan-interface ip-address ' + gateway + '.254.0.1 255.0.0.0')
        re = self.readuntil('(config-vlan-' + vlan + ')#')
        if '%' in re and '%Entry exists' not in re:
            return False,re
        else:
            return True,''

    def doConfigPon(self,vlan,slot,port):
        self.log('configPon vlan '+ vlan + ' '+ slot + '/' + port)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface pon ' + slot + '/' + port)
        self.readuntil('(config-if-pon-' + slot + '/' + port +')#')
        self.send('vlan batch ' + vlan + ' transparent')
        re = self.readuntil('(config-if-pon-' + slot + '/' + port +')#')
        if '%' in re:
            return False,re
        else:
            return True,''

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
            key = '{}/{}/{}'.format(slot,port,device)
            if not allKey.__contains__(key) :
                allKey.append(key)
            version = self.getCcmtsVersion(key)
            self.log('{}:{}'.format(key,version))
            allVersion[key] = version
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
        return allCmts,allKey,allVersion

    def checkCmtsUpgradeStatus(self,slot,port,device):
        key = '{}/{}/{}'.format(slot,port,device)
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('show mdu image-upgrade-status interface {} | include Progress   :'.format(key))
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
        while True:
            for slot,portMap in self.allCmts.items():
                for port,deviceList in portMap.items():
                    for device in deviceList:
                        key =  '{}/{}/{}'.format(slot,port,device)
                        if not allKey.__contains__(key) :
                            allKey.append(key)
                        if not upgradeStatus.has_key(key) :
                            state,finish,result = self.checkCmtsUpgradeStatus(slot,port,device)
                            if state:
                                upgradeStatus[key] = state
                                self.log('{} upgrade state :{}'.format(key,state),cmts=slot + '/' + port + '/' + device)
                            else :
                                if finish:
                                    upgradeStatus[key] = state
                                    self.log('{} upgrade state :{}'.format(key,state),cmts=slot + '/' + port + '/' + device)
                                else :
                                    self.log('{} upgrade not finish{}'.format(key,result),cmts=slot + '/' + port + '/' + device)
            self.log('allKey:{};upgradeStatus{}'.format(len(allKey),len(upgradeStatus)))
            if len(allKey) == len(upgradeStatus):
                return
            time.sleep(30)



    def doClearOnuIp(self,vlan,slot,port,device):
        self.log('doClearOnuIp vlan '+ vlan + ' ' + slot + '/' + port + '/' + device,cmts=slot + '/' + port + '/' + device,headName='clearResult')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface ccmts ' + slot + '/' + port + '/' + device)
        self.readuntil('(config-if-ccmts-' + slot + '/' + port + '/' + device + ')#')
        self.send('no onu-ipconfig cvlan ' + vlan)
        re = self.readuntil('(config-if-ccmts-' + slot + '/' + port + '/' + device + ')#')
        if '%' in re:
            self.log('doClearOnuIp error.',cmts=slot + '/' + port + '/' + device,headName='clearResult')
            return False,re
        else:
            self.log('doClearOnuIp success.',cmts=slot + '/' + port + '/' + device,headName='clearResult')
            return True,''

    def doClearPonVlanConfig(self,vlan,slot,port):
        self.log('doClearPonVlanConfig vlan '+ vlan + ' '+ slot + '/' + port,headName='clearResult')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('interface pon ' + slot + '/' + port)
        self.readuntil('(config-if-pon-' + slot + '/' + port +')#')
        self.send('no vlan batch ' + vlan + ' transparent')
        re = self.readuntil('(config-if-pon-' + slot + '/' + port +')#')
        if '%' in re:
            return False,re
        else:
            return True,''

    def doClearVlanConfig(self,vlan):
        self.log('doClearVlanConfig vlan '+ vlan,headName='clearResult')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('vlan ' + vlan)
        self.readuntil('(config-vlan-' + vlan + ')#')
        self.send('no vlan-interface')
        re = self.readuntil('(config-vlan-' + vlan + ')#')
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
        for slot, portMap in self.allCmts.items():
            for port, deviceList in portMap.items():
                for device in deviceList:
                    key = '{}/{}/{}'.format(slot,port,device)
                    self.log('reset cmts {}'.format(key),cmts=slot + '/' + port + '/' + device)
                    self.send('interface ccmts ' + key,)
                    self.readuntil('(config-if-ccmts-{})#'.format(key))
                    self.send('reset')
                    self.readuntil('(config-if-ccmts-{})#'.format(key))
    def clearConfig(self,vlan):
        self.log('clearConfig',headName='clearResult')
        for slot,portMap in self.allCmts.items():
            for port,deviceList in portMap.items():
                #for device in deviceList:
                    #state,msg = self.doClearOnuIp(vlan,slot,port,device)
                    #if not state :
                    #    self.writeResult(msg)
                state,msg = self.doClearPonVlanConfig(vlan,slot,port)
                if not state :
                    self.writeResult(msg)
        state,msg = self.doClearVlanConfig(vlan)
        if not state:
            self.writeResult(msg)
    def doResetCmts(self):
        self.log('doResetCmts',headName='clearResult')
        bArray,bKeys,allVersion = self.getAllOnlineCmts()
        self.log('online cmts count(' + `len(bKeys)` + ')')
        self.resetCmts()
        while True:
            nbArray,nbKeys,allVersion = self.getAllOnlineCmts()
            self.log('online cmts count before reset(' + `len(bKeys)` + ') after reset(' + `len(nbKeys)` + ')')
            if len(bKeys) == len(nbKeys) :
                for key,version in allVersion.items():
                    self.listView.setData('{}_{}'.format(self.host,key), 'result', version)
                break
            time.sleep(30)





from ftplib import FTP
import datetime
import os
import traceback

from UpgradeOlt import UpgradeOlt

class UpgradeOltFtpClient(UpgradeOlt):
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
            self.doStep(2,self.collectData,args=['before'])
            self.doStep(3,self.openFtpServer)
            self.doStep(4,self.loginIntoFtp)
            isActiveAndStandby,mainFile,otherFiles = self.allImageTypeAndFileName()
            if mainFile == 'mpub':
                self.doStep(5,self.downloadImage,args=[isActiveAndStandby,mainFile,otherFiles])
                # for olt version 1.9.0  after download all image must reconnect telnet
                self.reconnect()
                self.doStep(6,self.syncFile)
                self.doStep(7,self.upgradeServiceBootrom())
                self.doStep(8,self.rebootOlt)
                self.doStep(9,self.upgradeMpubBootrom)
            else:
                self.doStep(5,self.downloadImage,args=[isActiveAndStandby,mainFile,otherFiles])
                # for olt version 1.9.0  after download all image must reconnect telnet
                self.reconnect()
                self.sleepT(5)
                self.doStep(6,self.syncFile)
                self.doStep(7,self.upgradeAllBootrom)
            self.doStep(10,self.rebootOlt)
            self.writeResult('upgrade success')
        except BaseException, msg:
            if 'An established connection was aborted by the software in your host machine' in msg:
                args=[self.isAAA,self.userName,self.password,self.enablePassword,self.appPath,self.logPath,self.sheetW,self.excelRow,self.listView,self.host]
                self.addRetry(args,step=self.step)
            self.log(`msg`)
            self.writeResult(`msg`)
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
    def doCollectData(self):
        try:
            self.collectData('after')
        except BaseException, msg:
            self.log(`msg`)
            print 'traceback.format_exc():\n%s' % traceback.format_exc()

    def connect(self,host,isAAA,userName,password,enablePassword,appPath,logPath,sheetW,excelRow,listView):
        print 'connect to host ' + host
        try:
            self.ftpUserName = 'update'
            self.ftpPassword = 'update123'
            self.mpuAppDir = 'tffs0/app'
            self.otherAppDir = 'yaffs2/app'
            self.initListView(listView)
            self.initExcel(sheetW,excelRow)
            self.initLog(logPath,host)
            self.setAppPath(appPath)
            self.setTelnetArg(host,isAAA,userName,password,enablePassword)
        except BaseException, msg:
            print msg
            msg = 'telnet connecting failed'
            self.writeResult(msg)
            print 'traceback.format_exc():\n%s' % traceback.format_exc()

    def openFtpServer(self):
        self.log('openFtpServer')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('ftp server enable')
        self.readuntil('(config)#')
        self.send('ftp-password ' + self.ftpPassword)
        self.readuntil('(config)#')
        self.writeResult('openFtpServer success')

    def closeFtpServer(self):
        self.log('closeFtpServer')
        self.send('end')
        self.readuntil('#')
        self.send('configure terminal')
        self.readuntil('(config)#')
        self.send('ftp server disable')
        self.readuntil('(config)#')

    def loginIntoFtp(self):
        self.ftp = FTP()
        self.ftp.connect(self.host, 21)
        self.ftp.login(self.ftpUserName, self.ftpPassword)
        self.log(self.ftp.getwelcome())
        rootDirs = self.ftp.nlst()
        if 'yaffs2' not in rootDirs:
            self.log('yaffs2 is not exist.')
            self.otherAppDir = self.mpuAppDir
        self.writeResult('loginIntoFtp success')

    def doDownload(self,type, file):
        self.log('upload ' + type)
        self.ftp.cwd('/')
        if type in (self.getMainBoardTypes()) :
            self.log(self.ftp.cwd(self.mpuAppDir))
        else :
            self.log(self.ftp.cwd(self.otherAppDir))
        if not self.appPath.endswith('/'):
            self.appPath += '/'
        filePath = self.appPath + file
        if os.path.exists(filePath):
            fileList = self.ftp.nlst()
            self.log(`fileList`)
            if file in fileList:
                self.log(self.ftp.delete(file))
            bufsize = 1024
            fp = open(filePath, 'rb')
            self.log('Transfer ' + type + '.bin start')
            info = self.ftp.storbinary('STOR ' + file, fp, bufsize)
            self.log(info)
            fp.close()
            if info != '226 Transfer complete':
                raise Exception("upload image file error[" + file + ']')
        else :
            self.log('upload image file[' + filePath + '] not exists.')

    def downloadImage(self,isActiveAndStandby,mainFile,otherFiles):
        self.log('downloadAllImage')
        try:
            self.checkFreeSize(isActiveAndStandby,mainFile,otherFiles)
            self.doDownload(mainFile,mainFile + '.bin')
            for f in otherFiles:
                self.doDownload(f ,f + '.bin')
            self.writeResult('downloadAllImage success')
            return True
        except Exception, msg:
            self.log(`msg`)
            self.writeResult(`msg`)
            return False




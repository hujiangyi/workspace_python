#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
# deliverTest

import sys
sys.path.append("C:\WINDOWS\SYSTEM32\python27.zip")
sys.path.append("C:\Python27\DLLs")
sys.path.append("C:\Python27\lib")
sys.path.append("C:\Python27\lib\plat-win")
sys.path.append("C:\Python27\lib\lib-tk")
sys.path.append("C:\Python27")
sys.path.append("C:\Python27\lib\site-packages")

import serial
import re
import os
import time
import pysnmp
from pysnmp.hlapi import *


res = ''
err = ''
ss = serial.Serial()
#obIp='192.168.0.10'
obIp='192.168.0.10'
obMask='255.255.255.0'
ftpIp='192.168.0.200'
ftpUserName='suma'
ftpPassword='sumavision'

def connect(p='COM1'):
    print 'connect to serial port ' + p
    try:
        ss.port = p
        ss.baudrate  = 9600
        print 'open serial port ' + p
        ss.open()
    except BaseException,msg:
        print msg
        msg = 'Serial port connecting failed'
        err = msg
        raise Exception(msg)

def close():
    try:
        print 'close serial port'
        ss.close()
    except Exception,msg:
        print msg
        msg = 'Serial port close failed'
        err = msg
        raise Exception(msg)

def send(cmd):
    terminator = '\r'
    cmd = str(cmd)
    cmd += terminator
    try:
        msg = cmd
        ss.write(cmd)
    except Exception,msg:
        print msg
        raise Exception("Serial port write error!")

def read(delay=1):
    time.sleep(delay)
    n = ss.inWaiting()
    str = ss.read(n)
    return str

def readuntil(waitstr='xxx', timeout=0):
    tmp=""
    if timeout != 0:
        delay = 0.0
        while delay <= timeout:
            tmp += read()
            if waitstr in tmp:
                return tmp
            delay += 1
        raise Exception("wait str timeout")
    else:
        while 1:
            tmp += read()
            if needLogin(tmp) :
                send('')
                tmp += read()
            if waitstr in tmp:
                return tmp

def readuntilII(waitstr='xxx', timeout=0):
    tmp=""
    if timeout != 0:
        delay = 0.0
        while delay <= timeout:
            tmp += read()
            if waitstr in tmp:
                return tmp
            delay += 1
        raise Exception("wait str timeout")
    else:
        while 1:
            tmp += read()
            if waitstr in tmp:
                return tmp

def result():
    global res
    return res

def error():
    global err
    return err

def sleepT(delay):
    print 'sleep ' + str(delay) + 'sec start'
    time.sleep(delay)
    print 'sleep ' + str(delay) + 'sec end'

def needLogin(str):
    global res
    res = "";
    res += str
    if 'assword:' in str:
        try:
            print 'CLI timeout need login.'
            send('')
            res += readuntilII(waitstr='assword:', timeout=60);
            send('suma')
            res += readuntilII('PN8600>')
            send('en')
            res += readuntilII('Enable Password:')
            send('suma')
            res += readuntilII('PN8600#')
            return True
        except Exception,msg:
            print msg
            err = msg

def eraseandreboot():
    global res
    res = "";
    try:
        print 'erase startup-config'
        send('end')
        res += readuntil('PN8600#')
        send('erase startup-config')
        res += readuntil('Are you sure?(y/n) [n]')
        send('y')
        res += readuntil('PN8600#')
        print 'system reboot'
        send('system reboot')
        res += readuntil('System will reboot!')
        send('y')
        res += readuntil('System now is rebooting,please wait.')
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def mpuStarted():
    global res
    res = "";
    str = read()
    res += str
    if 'assword:' in str:
        try:
            print 'Mpu started'
            send('')
            res += readuntilII(waitstr='assword:', timeout=30);
            send('suma')
            res += readuntilII('PN8600>')
            send('en')
            res += readuntilII('Enable Password:')
            send('suma')
            res += readuntilII('PN8600#')
            return True
        except Exception,msg:
            print msg
            err = msg
            return False
    else :
        err = 'Mpu not ready'
        return False

def sendF2():
    print ss.port
    global res
    res = "";
    try:
        print 'Wait stop auto-boot'
        res += readuntil(waitstr='stop auto-boot', timeout=30);
        cmd = '\033OQ'
        print 'Send F2'
        while True :
            send(cmd)
            tmp = read()
            print tmp
            res += tmp
            if '[PN8600 Boot]:' in tmp :
                break
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def startUpArg(mpuType='MPUA'):
    import datetime
    global res
    res = "";
    binName = 'mpu.bin'
    print mpuType
    if  mpuType == 'MPUB':
        binName = 'mpub.bin'
    if  (mpuType == 'MEFC') or (mpuType == 'MEFD'):
        binName = 'mef.bin'
    if  (mpuType == 'MEUA') or (mpuType == 'MEUB') or (mpuType == 'MEFA') or (mpuType == 'MEFB'):
        binName = 'meu.bin'
    print binName
    try:
        send('p')
        res += readuntil('[PN8600 Boot]:')
        print 'Modify startup arg'
        send('c')
        res += readuntil('boot device          :')
        print '1'
        send('mottsec1')
        res += readuntil('processor number')
        print '2'
        send('0')
        res += readuntil('host name')
        print '3'
        send('host')
        res += readuntil('file name')
        print '4'
        send(binName)
        res += readuntil('inet on ethernet (e) :')
        print '5'
        send(obIp)
        res += readuntil('inet on backplane (b):')
        print '6'
        send('')
        res += readuntil('host inet (h)        :')
        print '7'
        send(ftpIp)
        res += readuntil('gateway inet (g)     :')
        print '8'
        send('')
        res += readuntil('user (u)             :')
        print '9'
        send(ftpUserName)
        res += readuntil('ftp password (pw) (blank = use rsh):')
        print '10'
        send(ftpPassword)
        res += readuntil('flags (f)            :')
        print '11'
        send('0x0')
        res += readuntil('target name (tn)     :')
        print '12'
        send('ads8308')
        res += readuntil('startup script (s)   :')
        print '13'
        send('')
        res += readuntil('other (o)            :')
        print '14'
        send('mottsec0')
        res += readuntil('[PN8600 Boot]:')
        print '15'
        send('p')
        res += readuntil('[PN8600 Boot]:')
        print '16'
        send('@')
        timestart = datetime.datetime.now()
        print 'waitstart:' + str(timestart)  
        print 'starting......'
        try:
            res += readuntil(waitstr="I'm MPU active", timeout=500)
            print res
            timestopmpu = datetime.datetime.now()
            print 'waitstopmpu:'+str(timestopmpu)
        except:
            print 'test twice!'
            print 'Wait stop auto-boot'
            res += readuntil(waitstr='stop auto-boot', timeout=30)
            timestop = datetime.datetime.now()
            print 'waitstop:'+str(timestop)
            cmd = '\033OQ'
            print 'Send F2'
            send('@')           

        print 'finish......'
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def assignBoard():
    global res
    res = "";
    try:
        send('end')
        res += readuntil('PN8600#')
        send('show board')
        boardInfo = readuntil(waitstr='PN8600#');
        res +=boardInfo
        send('configure terminal')
        res += readuntil('PN8600(config)#')
        bs = boardInfo.split('\r\n')
        for s in bs :
            if 'show board' in s :
                continue
            if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s :
                continue
            if '------' in s :
                continue
            if 'Total:' in s :
                continue
            if '#' in s :
                continue
            #print s
            slotid=s[2:4].strip()
            assignType=s[9:13].strip()
            presentType=s[26:33].strip()
            adminStatus=s[43:46]
            operationStatus=s[60:64]
            #print slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus
            if presentType == 'unknown':
                continue
            if presentType == '-':
                continue
            if assignType != '-':
                continue
            presentType=presentType[0:4]
            cmd='board assign ' + slotid + ' ' + presentType;
            send(cmd)
            res +=readuntil(waitstr='PN8600(config)#');
            cmd='board admin ' + slotid + ' is';
            send(cmd)
            res +=readuntil(waitstr='PN8600(config)#');
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def outbandIp():
    global res
    res = "";
    try:
        send('end')
        res += readuntil('PN8600#')
        send('configure terminal')
        res += readuntil('PN8600(config)#')
        send('outband ip-address ' + obIp + ' ' + obMask)
        outbandIp= readuntil('PN8600(config)#')
        res+=outbandIp
        if '%u' in outbandIp.lower() :
            raise Exception("set outbandIp error")
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def rtcTime():
    global res
    res = "";
    try:
        import datetime
        i = datetime.datetime.now()
        year = i.year
        month=i.month
        day=i.day
        hour=i.hour
        minute=i.minute
        second=i.second
        cmd='datetime ' + str(year) + ' ' + str(month) + ' ' + str(day) + ' ' + str(hour) + ' ' + str(minute) + ' ' + str(second)
        send('end')
        res += readuntil('PN8600#')
        send('configure terminal')
        res += readuntil('PN8600(config)#')
        send(cmd)
        rtcTime= readuntil('PN8600(config)#')
        res+=rtcTime
        if '%' in rtcTime :
            raise Exception("set rtcTime error")
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def doDownload(type,file):
    global res
    res = "";
    send('end')
    res += readuntil('PN8600#')
    cmd = 'download ' + type + ' ' + ftpIp + ' ' + ftpUserName + ' ' + ftpPassword + ' ' + file
    print cmd
    send(cmd)
    res += readuntil('PN8600#')
    sleepT(10)
    send('show file transfering-status')
    fts = readuntil('PN8600#')
    print fts
    res +=fts
    while 'successfully' not in fts :
        if 'transfer failed' in fts :
            raise Exception(file + " transfer failed")
        sleepT(10)
        send('show file transfering-status')
        fts = readuntil('PN8600#')
        print fts
        res +=fts

def downloadImage():
    print 'downloadImage'
    global res
    res = "";
    try:
        pwd = sp()
        send('end')
        print 'end'
        res += readuntil('PN8600#')
        print 'PN8600#'
        send('super')
        print 'super'
        res += readuntilII('Super Password:')
        print 'Super Password:'
        send(pwd)
        res += readuntil('PN8600(config-super)#')
        print 'PN8600(config-super)#'
        send('outband rate disable')
        print 'outband rate disable'
        res += readuntil('PN8600(config-super)#')
        print 'PN8600(config-super)#'
        send('end')
        print 'end'
        res += readuntil('PN8600#')
        print 'PN8600#'
        send('show system')
        print 'show system'
        systemInfo = readuntil(waitstr='PN8600#');
        print 'PN8600#'
        res += systemInfo
        si = systemInfo.split('\r\n')
        sysObjectId = ''
        for s in si :
            if 'System total service slots' in s :
                #print s
                indexStart = s.index(':')
                indexEnd = len(s)
                if indexStart == -1:
                    raise Exception('Read olt type error')
                ts = s[indexStart + 1:indexEnd].strip()
                totalSlot = int(ts)
                #print 'totalSlot:' + str(totalSlot)
                if totalSlot == 3 :
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.2'
                elif totalSlot == 8 :
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.3'
                elif totalSlot == 18 :
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.1'
                else :
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.2.x'
        send('show board')
        boardInfo = readuntil(waitstr='PN8600#');
        #print boardInfo
        res += boardInfo
        send('configure terminal')
        res += readuntil('PN8600(config)#')
        bs = boardInfo.split('\r\n')
        for s in bs :
            if 'show board' in s :
                continue
            if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s :
                continue
            if '------' in s :
                continue
            if 'Total:' in s :
                continue
            if '#' in s :
                continue
            slotid=s[2:4].strip()
            assignType=s[9:13].strip()
            presentType=s[26:33].strip()
            adminStatus=s[43:46]
            operationStatus=s[60:64]    
            #print slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus
            if '*' in slotid :
                if assignType == 'mpub':  
                    #mpub
                    print 'download mpub'
                    doDownload('mpub','mpub.bin')
                    print 'download epu'
                    doDownload('epu','epu.bin')
                    print 'download xgu'
                    doDownload('xgu','xgu.bin')
                    print 'download bootrom'
                    doDownload('bootrom','bootrom.bin')
                    print 'download bootrom-e500'
                    doDownload('bootrom-e500','bootrom-e500.bin')
                else :    
                    if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.1' :
                        #8601 
                        print 'download mpu'
                        doDownload('mpu','mpu.bin')
                        print 'download epu'
                        doDownload('epu','epu.bin')
                        print 'download xgu'
                        doDownload('xgu','xgu.bin')
                        print 'download bootrom'
                        doDownload('bootrom','bootrom.bin')
                        print 'download bootrom-e500'
                        doDownload('bootrom-e500','bootrom-e500.bin')
                    if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.2' :
                        #8602 
                        print 'download mpu'
                        doDownload('mpu','mpu.bin')
                        print 'download epu'
                        doDownload('epu','epu.bin')
                        print 'download xgu'
                        doDownload('xgu','xgu.bin')
                        print 'download bootrom'
                        doDownload('bootrom','bootrom.bin')
                        print 'download bootrom-e500'
                        doDownload('bootrom-e500','bootrom-e500.bin')
                    elif sysObjectId == '1.3.6.1.4.1.32285.11.2.1.3' :
                        #8603 
                        print 'download mpu'
                        doDownload('mpu','mpu.bin')
                        print 'download epu'
                        doDownload('epu','epu.bin')
                        print 'download xgu'
                        doDownload('xgu','xgu.bin')
                        print 'download bootrom'
                        doDownload('bootrom','bootrom.bin')
                        print 'download bootrom-e500'
                        doDownload('bootrom-e500','bootrom-e500.bin')
                    else :
                        #other 8602e 8602ef
                        print 'download mef'
                        doDownload('mef','mef.bin')
                        print 'download bootrom'
                        doDownload('bootrom','bootrom.bin')
        return True
    except Exception,msg:
        print msg
        err = msg
        return False


def syncFile():
    sleepT(3)
    print 'sync config file'
    send('sync config file')
    res += readuntil('Are you sure?(y/n) [n]')
    send('y')
    res += readuntil('PN8600#')
    send('show file sync-status')
    tmp = read()
    print tmp
    while 'synchronize config successfully' not in tmp:
        sleepT(10)
        send('show file sync-status')
        tmp = read()
        res += tmp
        print tmp
    print 'sync app file'
    send('sync app file')
    res += readuntil('Are you sure?(y/n) [n]')
    send('y')
    res += readuntil('PN8600#')
    send('show file sync-status')
    tmp = read()
    print tmp
    while 'synchronize software successfully' not in tmp:
        sleepT(10)
        send('show file sync-status')
        tmp = read()
        res += tmp
        print tmp
    sleepT(3)

def upgradeBootrom():
    global res
    res = "";
    try:
        send('end')
        res += readuntil('PN8600#')
        send('show system')
        print 'show system'
        systemInfo = readuntil(waitstr='PN8600#');
        print 'PN8600#'
        res += systemInfo
        si = systemInfo.split('\r\n')
        sysObjectId = ''
        for s in si :
            if 'System total service slots' in s :
                #print s
                indexStart = s.index(':')
                indexEnd = len(s)
                if indexStart == -1:
                    raise Exception('Read olt type error')
                ts = s[indexStart + 1:indexEnd].strip()
                totalSlot = int(ts)
                #print 'totalSlot:' + str(totalSlot)
                if totalSlot == 8 or totalSlot == 18 :
                    syncFile()
        send('show board')
        boardInfo = readuntil(waitstr='PN8600#');
        res +=boardInfo
        bs = boardInfo.split('\r\n')
        for s in bs :
            if 'show board' in s :
                continue
            if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s :
                continue
            if '------' in s :
                continue
            if 'Total:' in s :
                continue
            if '#' in s :
                continue
            print s
            slotid=s[2:4].strip()
            assignType=s[9:13].strip()
            presentType=s[26:33].strip()
            adminStatus=s[43:46]
            operationStatus=s[60:64]
            #print slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus
            if '*' in slotid :
                slotid = slotid[0:1]
            if operationStatus == 'IS':
                cmd = 'upgrade bootrom slot ' + slotid
                send(cmd)
                upgraderesult = readuntil(waitstr='PN8600#');
                res+=upgraderesult
                print res
                if '%' in upgraderesult :
                    raise Exception('slot ' + slotid + " upgrade bootrom failed")
                else:
                    print 'upgradeBootrom success! ' + cmd
        return True
    except Exception,msg:
        print msg
        err = msg
        return False
    
def writefileandreboot():
    print 'writefileandreboot'
    global res
    res = "";
    try:
        send('end')
        res += readuntil('PN8600#')
        print 'write file'
        send('write file')
        sleepT(3)
        res += readuntil('Are you sure?(y/n) [n]')
        sleepT(3)
        send('y')
        res += readuntil('PN8600#')
        print 'system reboot'
        send('system reboot')
        res += readuntil('System will reboot!')
        send('y')
        res += readuntil('System now is rebooting,please wait.')
        return True
    except Exception,msg:
        print msg
        err = msg
        return False


mainBoard = '1'
oosBoard = '1'
def isAllBoardOnline():
    global mainBoard
    global oosBoard
    send('show board')
    boardInfo = readuntil(waitstr='PN8600#');
    print boardInfo
    bs = boardInfo.split('\r\n')
    length = len(bs) - 6
    print 'board count:' + str(length)
    skip = [1]
    if length==1:
        skip = [1]
    if length==3:
        skip = [1]
    if length==8:
        skip = [4,5]
    if length==18:
        skip = [9,10]
    for s in bs :
        if 'show board' in s :
            continue
        if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s :
            continue
        if '------' in s :
            continue
        if 'Total:' in s :
            continue
        if '#' in s :
            continue
        #print s
        slotid=s[2:4].strip()
        assignType=s[9:13].strip()
        presentType=s[26:33].strip()
        adminStatus=s[43:46].strip()
        operationStatus=s[60:64].strip()          
        if '*' in slotid :
            slotid = slotid[0:1]
            mainBoard = slotid
        if assignType == '-':
            continue
        if int(slotid) in skip:
            continue
        print slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus
        if operationStatus == 'OOS':
            oosBoard = slotid
            print 'Board online error slotid is ' + slotid
            return False
    return True

def boardInfo():
    global res
    global mainBoard
    res = "";
    try:
        send('end')
        res += readuntil('PN8600#')
        while True:
            sleepT(10)
            if isAllBoardOnline():
                break
            oid = '1.3.6.1.4.1.17409.2.3.1.3.1.1.10.1.' + mainBoard
            g = getCmd(SnmpEngine(),CommunityData('public'),UdpTransportTarget((obIp,161)),ContextData(),ObjectType(ObjectIdentity(oid)))
            a = next(g)
            msg = str(a[0])
            if 'No SNMP response received before timeout' in msg :
                raise Exception(msg)
            if int(a[3][0].__getitem__(1)) > 30000 :
                raise Exception('The inspection time is more than 5 minutes')
        send('show board')
        boardInfo = readuntil(waitstr='PN8600#');
        res += boardInfo
        bs = boardInfo.split('\r\n')
        for s in bs :
            if 'show board' in s :
                continue
            if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s :
                continue
            if '------' in s :
                continue
            if 'Total:' in s :
                continue
            if '#' in s :
                continue
            #print s
            slotid=s[2:4].strip()
            assignType=s[9:13].strip()
            presentType=s[26:33].strip()
            adminStatus=s[43:46]
            operationStatus=s[60:64]      
            if '*' in slotid :
                slotid = slotid[0:1]
            if assignType == '-':
                continue
            #print slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus
            cmd = 'show board ' + slotid
            send(cmd)
            res += readuntil(waitstr='PN8600#');
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def boardTemperature():
    global res
    global oosBoard
    res = "";
    try:
        send('end')
        res += readuntil('PN8600#')
        if not isAllBoardOnline():
            raise Exception('board online error ' + oosBoard)
        send('show temperature all')
        temperatureInfo = readuntil(waitstr='PN8600#');
        res += temperatureInfo
        bs = temperatureInfo.split('\r\n')
        for s in bs :
            if 'show temperature all' in s :
                continue
            if 'Slot Status Upper Lower Temperature.(C)' in s :
                continue
            if '------' in s :
                continue
            if '#' in s :
                continue
            #print s
            slotid=s[0:1].strip()
            temperature=s[20:26].strip()
            #print slotid + ' ' + temperature
            if temperature == '-':
                continue
            t = int(temperature)
            if t < 10 or t > 65 :
                raise Exception('Temperature error on slot ' + slotid + ' temperature is ' + temperature)
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

eponType = ['epua','epub','epuc','meua','meub','mefa','mefb','mefc','mefd',]
eponPortNum = {'epua' : 8,'epub' : 8,'epuc' : 16,'meua' : 16,'meub' : 8,'mefa' : 16,'mefb' : 8,'mefc' : 16,'mefd' : 8}
gponType = ['gpua']
gponPortNum = {'gpua' : 16}

def opticalModuleInfo():
    global res
    global oosBoard
    res = "";
    try:
        send('end')
        res += readuntil('PN8600#')
        if not isAllBoardOnline():
            raise Exception('board online error ' + oosBoard)
        send('show board')
        boardInfo = readuntil(waitstr='PN8600#');
        res += boardInfo
        send('configure terminal')
        res += readuntil('PN8600(config)#')
        bs = boardInfo.split('\r\n')
        for s in bs :
            if 'show board' in s :
                continue
            if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s :
                continue
            if '------' in s :
                continue
            if 'Total:' in s :
                continue
            if '#' in s :
                continue
            #print s
            slotid=s[2:4].strip()
            assignType=s[9:13].strip()
            presentType=s[26:33].strip()
            adminStatus=s[43:46]
            operationStatus=s[60:64]
            print slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus
            if assignType in eponType:
                #8602e 8602ef
                if '*' in slotid :
                    slotid = '0';
                num = eponPortNum[assignType]
                for i in range(1,num + 1) :
                    cmd = 'interface pon ' + slotid + '/' + str(i)
                    send(cmd)
                    res += readuntil('(config-if-pon-' + slotid + '/' + str(i) + ')#')
                    send('show optical-transceiver')
                    r = readuntil('(config-if-pon-' + slotid + '/' + str(i) + ')#')
                    if '% Unknown command.' in r :
                        send('show port optical-transceiver')
                        r = readuntil('(config-if-pon-' + slotid + '/' + str(i) + ')#')
                    res += r
                    if '%optical-transceiver not exists or get infomation failed' in r :
                        #raise Exception('optical-transceiver not exists or get infomation failed')
                        print 'optical-transceiver ' + slotid + '/' + str(i) + ' not exists or get infomation failed'
                        continue
                    ots = r.split('\r\n')
                    for ot in ots :
                        vendorName='null'
                        temperature='null'
                        voltage='null'
                        txPower='null'
                        length = len(ot)
                        if 'Vendor Name' in ot :
                            vendorName = ot[33:length].strip()
                            print 'optical-transceiver ' + slotid + '/' + str(i) + ' vendorName ' + vendorName
                        if 'Temperature(C)' in ot :
                            temperature = ot[33:length].strip()
                            print 'optical-transceiver ' + slotid + '/' + str(i) + ' temperature ' + temperature
                            t = float(temperature)
                            if t < 10 or t > 60 :
                                raise Exception('optical-transceiver ' + slotid + '/' + str(i) + ' temperature error ' + temperature + 'C')
                        if 'Voltage(mV)' in ot :
                            voltage = ot[33:length].strip()
                            print 'optical-transceiver ' + slotid + '/' + str(i) + ' voltage ' + voltage
                            v = float(voltage)
                            if v < 3150 or v > 3450 :
                                raise Exception('optical-transceiver ' + slotid + '/' + str(i) + ' voltage error ' + voltage + 'mV')
                        if 'Tx power(dBm)' in ot :
                            txPower = ot[33:length].strip()
                            print 'optical-transceiver ' + slotid + '/' + str(i) + ' txPower ' + txPower
                            tx = float(txPower)
                            if tx < 2 or tx > 7 :
                                raise Exception('optical-transceiver ' + slotid + '/' + str(i) + ' txPower error ' + txPower + 'dBm')
        return True
    except Exception,msg:
        print msg
        err = msg
        return False


standards={'pn8601':[[2500,3800],[1700,3300],[1000,2300]],'pn8601mpub':[3000,3800],'pn8602':[[5000,7600],[4000,6000],[1500,5500]],'pn8603':[[5000,7600],[4000,6000],[1500,5500]],'pn8603mpub':[6500,7700],'pn8602e':[[15000,17000],[12000,14000],[11000,13000]]}

def checkFanSpeed(standard):
    global res
    send('show fan status')
    print 'show fan status'
    fanStates = readuntil('PN8600(config)#')
    print 'PN8600(config)#'
    res += fanStates
    states = fanStates.split('\r\n')
    for s in states :
        if 'Fan real speed' in s :
            indexStart = s.index(':')
            indexEnd = s.index('(rpm)')
            if indexStart == -1 or indexEnd == -1 :
                raise Exception('Read fan speed error')
            print s
            fs = s[indexStart + 1:indexEnd].strip()
            fanSpeed = int(fs)
            if fanSpeed < standard[0] or fanSpeed > standard[1] :
                raise Exception('Read speed out of rang. standard:' + str(standard) + ' fanSpeed:' + str(fanSpeed))
                #return

def fanInfo():
    global res
    global mainBoard
    res = "";
    try:
        send('end')
        res += readuntil('PN8600#')
        send('show system')
        systemInfo = readuntil(waitstr='PN8600#');
        res += systemInfo
        si = systemInfo.split('\r\n')
        sysObjectId = ''
        for s in si :
            if 'System total service slots' in s :
                #print s
                indexStart = s.index(':')
                indexEnd = len(s)
                if indexStart == -1:
                    raise Exception('Read olt type error')
                ts = s[indexStart + 1:indexEnd].strip()
                totalSlot = int(ts)
                #print 'totalSlot:' + str(totalSlot)
                if totalSlot == 3 :
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.2'
                elif totalSlot == 8 :
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.3'
                elif totalSlot == 18 :
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.1'
                else :
                    sysObjectId = '1.3.6.1.4.1.32285.11.2.1.2.x'
        send('show board')
        boardInfo = readuntil(waitstr='PN8600#');
        #print boardInfo
        res += boardInfo
        send('configure terminal')
        res += readuntil('PN8600(config)#')
        bs = boardInfo.split('\r\n')
        for s in bs :
            if 'show board' in s :
                continue
            if 'Slot   Assign Type      Present Type     Admin Status     Operation Status' in s :
                continue
            if '------' in s :
                continue
            if 'Total:' in s :
                continue
            if '#' in s :
                continue
            slotid=s[2:4].strip()
            assignType=s[9:13].strip()
            presentType=s[26:33].strip()
            adminStatus=s[43:46]
            operationStatus=s[60:64]    
            #print slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus
            if '*' in slotid :
                '''
                snmp获取的方式虽好，但是存在于程序不是很兼容的问题，所以还是不要用了
                print 'start snmp ' + obIp
                oid = '1.3.6.1.2.1.1.2.0'
                g = getCmd(SnmpEngine(),CommunityData('public'),UdpTransportTarget((obIp,161)),ContextData(),ObjectType(ObjectIdentity(oid)))
                a = next(g)
                msg = str(a[0])
                print 'end snmp'
                if 'No SNMP response received before timeout' in msg :
                    raise Exception(msg)
                sysObjectId = a[3][0].__getitem__(1) 
                '''
                #print str(sysObjectId) + " " + assignType
                if assignType == 'mpub':  
                    if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.1' :
                        #8601
                        send('fan speed high')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8601mpub']) 
                    elif sysObjectId == '1.3.6.1.4.1.32285.11.2.1.3' :
                        #8603
                        send('fan speed high')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8603mpub'])
                else :    
                    if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.1' :
                        #8601
                        send('fan speed high')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8601'][0]) 
                        send('fan speed middle')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8601'][1]) 
                        send('fan speed low')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8601'][2]) 
                        send('fan speed auto')
                        res += readuntil('PN8600(config)#')
                    if sysObjectId == '1.3.6.1.4.1.32285.11.2.1.2' :
                        #8602
                        send('fan speed high')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8602'][0]) 
                        send('fan speed middle')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8602'][1]) 
                        send('fan speed low')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8602'][2]) 
                        send('fan speed auto')
                        res += readuntil('PN8600(config)#')
                    elif sysObjectId == '1.3.6.1.4.1.32285.11.2.1.3' :
                        #8603
                        send('fan speed high')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8603'][0]) 
                        send('fan speed middle')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8603'][1]) 
                        send('fan speed low')
                        res += readuntil('PN8600(config)#')
                        sleepT(20)
                        checkFanSpeed(standards['pn8603'][2]) 
                        send('fan speed auto')
                        res += readuntil('PN8600(config)#')
                    else :
                        #other
                        send('fan speed high')
                        print 'fan speed high'
                        res += readuntil('PN8600(config)#')
                        sleepT(60)
                        checkFanSpeed(standards['pn8602e'][0]) 
                        send('fan speed middle')
                        print 'fan speed middle'
                        res += readuntil('PN8600(config)#')
                        sleepT(60)
                        checkFanSpeed(standards['pn8602e'][1]) 
                        send('fan speed low')
                        print 'fan speed low'
                        res += readuntil('PN8600(config)#')
                        sleepT(60)
                        checkFanSpeed(standards['pn8602e'][2]) 
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def powerTest():
    global res
    global oosBoard
    res = "";
    try:
        print 'Power test'
        send('end')
        res += readuntil('PN8600#')
        if not isAllBoardOnline():
            raise Exception('board online error ' + oosBoard)
        return True
    except Exception,msg:
        print msg
        err = msg
        return False

def sp():
    import datetime
    i = datetime.datetime.now()
    year = i.year * 17
    month = (i.month + 12) * 19
    day = i.day +23
    pwd = year * 1000 + month * 100 + day * (day + 29) * 341 -7
    return str(pwd)
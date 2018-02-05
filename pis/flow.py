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
from pysnmp.hlapi import *

res = ''
err = ''
ss = serial.Serial()

def connect(p='COM3'):
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
    print 'sleep ' + int(delay) + 'sec start'
    time.sleep(delay)
    print 'sleep ' + int(delay) + 'sec end'

def needLogin(str):
    global res
    res = "";
    res += str
    if 'assword:' in str:
        try:
            print 'CLI timeout need login.'
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

def masterStandbySwitching():
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
        bs = boardInfo.split('\r\r\n')
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

mainBoard = '1'
oosBoard = '1'
def isAllBoardOnline():
    global mainBoard
    global oosBoard
    send('show board')
    boardInfo = readuntil(waitstr='PN8600#');
    bs = boardInfo.split('\r\r\n')
    length = len(bs) - 5
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
        #print slotid + ' ' + assignType + ' ' + presentType + ' ' + adminStatus + ' ' + operationStatus
        if operationStatus == 'OOS':
            oosBoard = slotid
            print 'Board online error slotid is ' + slotid
            return False
    return True

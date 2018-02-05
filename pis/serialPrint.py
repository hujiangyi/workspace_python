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

res = ''
ss = serial.Serial()

def result():
    global res
    return res;

def connect(p='COM3'):
    try:
        ss.port = p
        ss.baudrate  = 9600
        ss.open()
    except BaseException,e:
        msg = 'Serial port connecting failed'
        raise Exception(msg)

def close():
    try:
        ss.close()
    except:
        msg = 'Serial port close failed'
        raise Exception(msg)

def send(cmd):
    terminator = '\r'
    cmd = str(cmd)
    cmd += terminator
    try:
        msg = cmd
        ss.write(cmd)
    except:
        raise Exception("Serial port write error!")

def read():
    time.sleep(1)
    n = ss.inWaiting()
    str = ss.read(n)
    return str

def readuntil(waitstr='xxx', timeout=1):
    tmp=""
    if timeout:
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
def sendF2():
    global res
    res = "";
    try:
        res += readuntil(waitstr='stop auto-boot', timeout=30);
        cmd = '\033OQ'
        send(cmd)
        res += readuntil('[PN8600 Boot]:')
        return True
    except:
        return False
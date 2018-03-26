import xlrd
import xlwt
import pysnmp
from pysnmp.hlapi import *
from IPy import *
import traceback
import datetime
import os


def getNextSnmpDataHexStringSimple(o, ip, community, timeout=1, retry=0) :
    data = ''
    hexG = nextCmd(SnmpEngine(),CommunityData(community),UdpTransportTarget((ip,161),timeout,retry),ContextData(),ObjectType(ObjectIdentity(o)))
    hexA = next(hexG)
    msg = `hexA[0]`
    if 'No SNMP response received before timeout' in msg  or 'RequestTimedOut()' in msg:
        log(ip + ' No SNMP response received.' + o)
        return 'error'
    oc=hexA[3][0].__getitem__(1)
    data=''.join(['%.2x' % x for x in oc.asNumbers()])
    #log(ip + ' ' + mac + ' ' + data)
    return data

def getNextSnmpDataNumberSimple(o, ip, community, timeout=1, retry=0) :
    data = ''
    numberG = nextCmd(SnmpEngine(),CommunityData(community),UdpTransportTarget((ip,161),timeout,retry),ContextData(),ObjectType(ObjectIdentity(o)))
    numberA = next(numberG)
    msg = `numberA[0]`
    if 'No SNMP response received before timeout' in msg  or 'RequestTimedOut()' in msg:
        log(ip + ' No SNMP response received.' + o)
        return 'error'
    if not isinstance(numberA[3][0].__getitem__(1),pysnmp.proto.rfc1902.Integer) :
        log('data is error')
        return 'error'
    else :
        data=numberA[3][0].__getitem__(1).__index__()
        #log(ip + ' ' + mac + ' ' + `data`)
        return data

def getSnmpDataHexStringSimple(o, ip, community, timeout=1, retry=0):
    data = ''
    hexG = getCmd(SnmpEngine(), CommunityData(community), UdpTransportTarget((ip, 161), timeout, retry),
                   ContextData(), ObjectType(ObjectIdentity(o)))
    hexA = next(hexG)
    msg = `hexA[0]`
    if 'No SNMP response received before timeout' in msg or 'RequestTimedOut()' in msg:
        log( ip + ' No SNMP response received.' + o)
        return 'error'
    oc = hexA[3][0].__getitem__(1)
    data = ''.join(['%.2x' % x for x in oc.asNumbers()])
    # log(ip + ' ' + mac + ' ' + data)
    return data

def getSnmpDataNumberSimple(o, ip, community, timeout=1, retry=0):
    data = ''
    numberG = getCmd(SnmpEngine(), CommunityData(community), UdpTransportTarget((ip, 161), timeout, retry),
                      ContextData(), ObjectType(ObjectIdentity(o)))
    numberA = next(numberG)
    msg = `numberA[0]`
    if 'No SNMP response received before timeout' in msg or 'RequestTimedOut()' in msg:
        log(ip + ' No SNMP response received.' + o)
        return 'error'
    if not isinstance(numberA[3][0].__getitem__(1), pysnmp.proto.rfc1902.Integer):
        log('data is error')
        return 'error'
    else:
        data = numberA[3][0].__getitem__(1).__index__()
        # log(ip + ' ' + mac + ' ' + `data`)
        return data

def hexToDeci(hex):
    hexs = hex.split(':')
    re = None
    for h in hexs:
        deci = int(h,16)
        if re is not None :
            re = '{}.{}'.format(re,deci)
        else :
            re = '{}'.format(deci)
    return re

def log(str):
    str = '{}\t{}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'),str)
    print str
    logResultFile.write(str)
    logResultFile.write('\n')
    logResultFile.flush()
def run() :
    excel='CM.xls'
    resultExcel='CMresult.xls'
    rb = xlrd.open_workbook(excel)
    wb=xlwt.Workbook()
    sheetCount=len(rb.sheets())
    for si in range(sheetCount) :
        log('%%%%%%%%%%%%%%%%%%%%%%%%%%' + `si` + '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        sheetName = `si`
        sheetR=rb.sheet_by_index(si)
        sheetW=wb.add_sheet(sheetName)
        nrows = sheetR.nrows
        ncols=sheetR.ncols
        wi=0
        sheetW.write(wi,0,'ip')
        sheetW.write(wi,1,'mac')
        sheetW.write(wi,2,'managerIp')
        sheetW.write(wi,3,'cmcIndex')
        sheetW.write(wi,4,'cmIndex')
        sheetW.write(wi,5,'equalizationData')
        sheetW.write(wi,6,'upChannelId')
        sheetW.write(wi,7,'upChannelFreq')
        sheetW.write(wi,8,'upChannelWidth')
        sheetW.write(wi,9,'upTxPower')
        sheetW.write(wi,10,'upRxPower')
        sheetW.write(wi,11,'upSignalNoise')
        wi+=1
        for i in range(nrows) :
            try :
                mac=sheetR.cell(i,2).value
                managerIp=sheetR.cell(i,0).value
                managerCommunity=sheetR.cell(i,1).value
                cmcIndex=sheetR.cell(i,4).value
                if mac == 'cmMac' :
                    continue
                macDeci = hexToDeci(mac)

                cmIndexOid = '1.3.6.1.2.1.10.127.1.3.7.1.2.{}'.format(macDeci)
                cmIndex = getSnmpDataNumberSimple(cmIndexOid, managerIp, managerCommunity)
                ipOid = '1.3.6.1.2.1.10.127.1.3.3.1.3.{}'.format(cmIndex)
                ipHex = getSnmpDataHexStringSimple(ipOid, managerIp, managerCommunity )
                if ipHex == None or ipHex == '':
                    ipOid = '1.3.6.1.2.1.10.127.1.3.3.1.21.{}'.format(cmIndex)
                    ipHex = getSnmpDataHexStringSimple(ipOid, managerIp, managerCommunity )
                ip = IPint(*parseAddress('0x{}'.format(ipHex))).strCompressed()
                if ip!='' and ip != '0.0.0.0' and 'cmIp' not in ip:
                    log(ip + ' ' + mac + ' ' + managerIp + ' ' + managerCommunity)
                    equalizationDataOid = '1.3.6.1.2.1.10.127.1.2.2.1.17'
                    equalizationData = getNextSnmpDataHexStringSimple(equalizationDataOid, ip, 'public')
                    if 'error' == equalizationData :
                        continue
                    upChannelIdOid = '1.3.6.1.2.1.10.127.1.1.2.1.1'
                    upChannelId = getNextSnmpDataNumberSimple(upChannelIdOid, ip, 'public')
                    upChannelFreqOid = '1.3.6.1.2.1.10.127.1.1.2.1.2'
                    upChannelFreq = getNextSnmpDataNumberSimple(upChannelFreqOid, ip, 'public')
                    upChannelWidthOid = '1.3.6.1.2.1.10.127.1.1.2.1.3'
                    upChannelWidth = getNextSnmpDataNumberSimple(upChannelWidthOid, ip, 'public')
                    upTxPowerOid = '1.3.6.1.2.1.10.127.1.2.2.1.3'
                    upTxPower = getNextSnmpDataNumberSimple(upTxPowerOid, ip, 'public')
                    upRxPowerOid = '1.3.6.1.2.1.10.127.1.3.3.1.6.{}'.format(cmIndex)
                    upRxPower = getSnmpDataNumberSimple(upRxPowerOid, managerIp, managerCommunity, 5, 1)
                    upSignalNoiseOid = '1.3.6.1.2.1.10.127.1.3.3.1.13.{}'.format(cmIndex)
                    upSignalNoise = getSnmpDataNumberSimple(upSignalNoiseOid, managerIp, managerCommunity, 5, 1)

                    sheetW.write(wi,0,ip)
                    sheetW.write(wi,1,mac)
                    sheetW.write(wi,2,managerIp)
                    sheetW.write(wi,3,cmcIndex)
                    sheetW.write(wi,4,cmIndex)
                    sheetW.write(wi,5,equalizationData)
                    sheetW.write(wi,6,upChannelId)
                    sheetW.write(wi,7,upChannelFreq)
                    sheetW.write(wi,8,upChannelWidth)
                    sheetW.write(wi,9,upTxPower)
                    sheetW.write(wi,10,upRxPower)
                    sheetW.write(wi,11,upSignalNoise)
                    wi+=1
            except Exception, msg:
                log('traceback.format_exc():\n%s' % traceback.format_exc())
        wb.save(resultExcel)
    wb.save(resultExcel)


logPath = 'log/{}/'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
os.makedirs(logPath)
logResultFile = open('{}logFile.log'.format(logPath), "w")
run()
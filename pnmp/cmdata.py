import xlrd
import xlwt
import pysnmp
from pysnmp.hlapi import *

def getSnmpDataHexString(oid,ip,community) :
    data = {}
    g = nextCmd(SnmpEngine(),CommunityData(community),UdpTransportTarget((ip,161),1,0),ContextData(),ObjectType(ObjectIdentity(o)))
    count=0
    while True:
        a = next(g)
        msg = `a[0]`
        if 'No SNMP response received before timeout' in msg  or 'RequestTimedOut()' in msg:
            print ip + ' No SNMP response received'
            break
        nOid = `a[3][0].__getitem__(0)`.replace(oid,'')
        if oid not in nOid :
            break
        count+=1
        oc=a[3][0].__getitem__(1)
        value=''.join(['%.2x' % x for x in oc.asNumbers()])
        data[nOid] = value
    return data

def getSnmpDataNumber(oid,ip,community) :
    data = {}
    g = nextCmd(SnmpEngine(),CommunityData(community),UdpTransportTarget((ip,161),1,0),ContextData(),ObjectType(ObjectIdentity(o)))
    count=0
    while True:
        a = next(g)
        msg = `a[0]`
        if 'No SNMP response received before timeout' in msg  or 'RequestTimedOut()' in msg:
            print ip + ' No SNMP response received'
            break
        nOid = `a[3][0].__getitem__(0)`.replace(oid,'')
        if oid not in nOid :
            break
        count+=1
        value=int(a[3][0].__getitem__(1))
        data[nOid] = value
    return data

def getSnmpDataHexStringSimple(o,ip,community,timeout=1,retry=0) :
    data = ''
    hexG = nextCmd(SnmpEngine(),CommunityData(community),UdpTransportTarget((ip,161),timeout,retry),ContextData(),ObjectType(ObjectIdentity(o)))
    hexA = next(hexG)
    msg = `hexA[0]`
    if 'No SNMP response received before timeout' in msg  or 'RequestTimedOut()' in msg:
        print ip + ' No SNMP response received.' + o
        return 'error'
    oc=hexA[3][0].__getitem__(1)
    data=''.join(['%.2x' % x for x in oc.asNumbers()])
    #print ip + ' ' + mac + ' ' + data
    return data

def getSnmpDataNumberSimple(o,ip,community,timeout=1,retry=0) :
    data = ''
    numberG = nextCmd(SnmpEngine(),CommunityData(community),UdpTransportTarget((ip,161),timeout,retry),ContextData(),ObjectType(ObjectIdentity(o)))
    numberA = next(numberG)
    msg = `numberA[0]`
    if 'No SNMP response received before timeout' in msg  or 'RequestTimedOut()' in msg:
        print ip + ' No SNMP response received.' + o
        return 'error'
    if not isinstance(a[3][0].__getitem__(1),pysnmp.proto.rfc1902.Integer) :
        print 'data is error'
        return 'error'
    else :
        data=numberA[3][0].__getitem__(1).__index__()
        #print ip + ' ' + mac + ' ' + `data`
        return data

def run() :
    excel='CM.xls'
    resultExcel='CMresult.xls'
    rb = xlrd.open_workbook(excel)
    wb=xlwt.Workbook()
    sheetCount=len(rb.sheets())
    for si in range(sheetCount) :
        print '%%%%%%%%%%%%%%%%%%%%%%%%%%' + `si` + '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
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
            ip=sheetR.cell(i,3).value
            if ip!='' and ip != '0.0.0.0' and 'IP' not in ip:
                mac=sheetR.cell(i,2).value
                managerIp=sheetR.cell(i,0).value
                managerCommunity=sheetR.cell(i,1).value
                cmcIndex=sheetR.cell(i,4).value
                cmIndex=sheetR.cell(i,5).value
                print ip + ' ' + mac + ' ' + managerIp + ' ' + managerCommunity
                equalizationDataOid = '1.3.6.1.2.1.10.127.1.2.2.1.17' 
                equalizationData = getSnmpDataHexStringSimple(equalizationDataOid,ip,'public')
                if 'error' == equalizationData : 
                    continue
                upChannelIdOid = '1.3.6.1.2.1.10.127.1.1.2.1.1' 
                upChannelId = getSnmpDataNumberSimple(upChannelIdOid,ip,'public')
                upChannelFreqOid = '1.3.6.1.2.1.10.127.1.1.2.1.2' 
                upChannelFreq = getSnmpDataNumberSimple(upChannelFreqOid,ip,'public')
                upChannelWidthOid = '1.3.6.1.2.1.10.127.1.1.2.1.3' 
                upChannelWidth = getSnmpDataNumberSimple(upChannelWidthOid,ip,'public')
                upTxPowerOid = '1.3.6.1.2.1.10.127.1.2.2.1.3' 
                upTxPower = getSnmpDataNumberSimple(upTxPowerOid,ip,'public')
                upRxPowerOid = '1.3.6.1.2.1.10.127.1.3.3.1.6.' + `cmIndex` 
                upRxPower = getSnmpDataNumberSimple(upRxPowerOid,managerIp,managerCommunity,5,1)
                upSignalNoiseOid = '1.3.6.1.2.1.10.127.1.3.3.1.13.' + `cmIndex` 
                upSignalNoise = getSnmpDataNumberSimple(upSignalNoiseOid,managerIp,managerCommunity,5,1)

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
        wb.save(resultExcel)
    wb.save(resultExcel)
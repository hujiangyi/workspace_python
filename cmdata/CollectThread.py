from threading import Thread

import pysnmp
from pysnmp.hlapi import *

class CollectThread (Thread) :
    def __init__(self,ip,mac,managerIp,managerCommunity,cmcIndex,cmIndex,sheetW,wi):
        Thread.__init__(self)
        self.ip = ip
        self.mac = mac
        self.managerIp = managerIp
        self.managerCommunity = managerCommunity
        self.cmcIndex = cmcIndex
        self.cmIndex = cmIndex
        self.sheetW = sheetW
        self.wi = wi
    def run(self):
        #print '{} start'.format(self.ip)
        equalizationData = ''
        upChannelId = ''
        upChannelFreq = ''
        upChannelWidth = ''
        upTxPower = ''
        upRxPower = ''
        upSignalNoise = ''
        try:
            equalizationDataOid = '1.3.6.1.2.1.10.127.1.2.2.1.17'
            equalizationData = self.getSnmpDataHexStringSimple(equalizationDataOid, self.ip, 'public')
            if 'error' == equalizationData:
                raise Exception('collect error')
            upChannelIdOid = '1.3.6.1.2.1.10.127.1.1.2.1.1'
            upChannelId = self.getSnmpDataNumberSimple(upChannelIdOid, self.ip, 'public')
            upChannelFreqOid = '1.3.6.1.2.1.10.127.1.1.2.1.2'
            upChannelFreq = self.getSnmpDataNumberSimple(upChannelFreqOid, self.ip, 'public')
            upChannelWidthOid = '1.3.6.1.2.1.10.127.1.1.2.1.3'
            upChannelWidth = self.getSnmpDataNumberSimple(upChannelWidthOid, self.ip, 'public')
            upTxPowerOid = '1.3.6.1.2.1.10.127.1.2.2.1.3'
            upTxPower = self.getSnmpDataNumberSimple(upTxPowerOid, self.ip, 'public')
            upRxPowerOid = '1.3.6.1.2.1.10.127.1.3.3.1.6.{}'.format(self.cmIndex)
            upRxPower = self.getSnmpDataNumberSimple(upRxPowerOid, self.managerIp, self.managerCommunity, 5, 1)
            upSignalNoiseOid = '1.3.6.1.2.1.10.127.1.3.3.1.13.{}'.format(self.cmIndex)
            upSignalNoise = self.getSnmpDataNumberSimple(upSignalNoiseOid, self.managerIp, self.managerCommunity, 5, 1)
        except BaseException, msg:
            str = msg
        finally:
            self.sheetW.write(self.wi, 0, self.ip)
            self.sheetW.write(self.wi, 1, self.mac)
            self.sheetW.write(self.wi, 2, self.managerIp)
            self.sheetW.write(self.wi, 3, self.cmcIndex)
            self.sheetW.write(self.wi, 4, self.cmIndex)
            self.sheetW.write(self.wi, 5, equalizationData)
            self.sheetW.write(self.wi, 6, upChannelId)
            self.sheetW.write(self.wi, 7, upChannelFreq)
            self.sheetW.write(self.wi, 8, upChannelWidth)
            self.sheetW.write(self.wi, 9, upTxPower)
            self.sheetW.write(self.wi, 10, upRxPower)
            self.sheetW.write(self.wi, 11, upSignalNoise)
            #print '{} end'.format(self.ip)

    def getSnmpDataHexString(self,o, ip, community):
        data = {}
        g = nextCmd(SnmpEngine(), CommunityData(community), UdpTransportTarget((ip, 161), 1, 0), ContextData(),
                    ObjectType(ObjectIdentity(o)))
        count = 0
        while True:
            a = next(g)
            msg = `a[0]`
            if 'No SNMP response received before timeout' in msg or 'RequestTimedOut()' in msg:
                print ip + ' No SNMP response received'
                break
            nOid = `a[3][0].__getitem__(0)`.replace(o, '')
            if o not in nOid:
                break
            count += 1
            oc = a[3][0].__getitem__(1)
            value = ''.join(['%.2x' % x for x in oc.asNumbers()])
            data[nOid] = value
        print ip + ' ' + community + ' ' + data
        return data

    def getSnmpDataNumber(self,o, ip, community):
        data = {}
        g = nextCmd(SnmpEngine(), CommunityData(community), UdpTransportTarget((ip, 161), 1, 0), ContextData(),
                    ObjectType(ObjectIdentity(o)))
        count = 0
        while True:
            a = next(g)
            msg = `a[0]`
            if 'No SNMP response received before timeout' in msg or 'RequestTimedOut()' in msg:
                print ip + ' No SNMP response received'
                break
            nOid = `a[3][0].__getitem__(0)`.replace(o, '')
            if o not in nOid:
                break
            count += 1
            value = int(a[3][0].__getitem__(1))
            data[nOid] = value
        # print ip + ' ' + mac + ' ' + data
        return data

    def getSnmpDataHexStringSimple(self,o, ip, community, timeout=1, retry=0):
        data = ''
        hexG = nextCmd(SnmpEngine(), CommunityData(community), UdpTransportTarget((ip, 161), timeout, retry),
                       ContextData(), ObjectType(ObjectIdentity(o)))
        hexA = next(hexG)
        msg = `hexA[0]`
        if 'No SNMP response received before timeout' in msg or 'RequestTimedOut()' in msg:
            print ip + ' No SNMP response received.' + o
            return 'error'
        oc = hexA[3][0].__getitem__(1)
        data = ''.join(['%.2x' % x for x in oc.asNumbers()])
        # print ip + ' ' + mac + ' ' + data
        return data

    def getSnmpDataNumberSimple(self,o, ip, community, timeout=1, retry=0):
        data = ''
        numberG = nextCmd(SnmpEngine(), CommunityData(community), UdpTransportTarget((ip, 161), timeout, retry),
                          ContextData(), ObjectType(ObjectIdentity(o)))
        numberA = next(numberG)
        msg = `numberA[0]`
        if 'No SNMP response received before timeout' in msg or 'RequestTimedOut()' in msg:
            print ip + ' No SNMP response received.' + o
            return 'error'
        if not isinstance(numberA[3][0].__getitem__(1), pysnmp.proto.rfc1902.Integer):
            print 'data is error'
            return 'error'
        else:
            data = numberA[3][0].__getitem__(1).__index__()
            # print ip + ' ' + mac + ' ' + `data`
            return data

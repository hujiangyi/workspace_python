from threading import Thread

import pysnmp
from pysnmp.hlapi import *

class CollectThreadIII (Thread) :
    def __init__(self,cmDataIII,cmList):
        Thread.__init__(self)
        self.cmDataIII = cmDataIII
        self.cmList = cmList
    def run(self):
        for cm in self.cmList:
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
                equalizationData = self.getSnmpDataHexStringSimple(equalizationDataOid, cm.ip, 'public')
                if 'error' == equalizationData:
                    raise Exception('collect error')
                upChannelIdOid = '1.3.6.1.2.1.10.127.1.1.2.1.1'
                upChannelId = self.getSnmpDataNumberSimple(upChannelIdOid, cm.ip, 'public')
                upChannelFreqOid = '1.3.6.1.2.1.10.127.1.1.2.1.2'
                upChannelFreq = self.getSnmpDataNumberSimple(upChannelFreqOid, cm.ip, 'public')
                upChannelWidthOid = '1.3.6.1.2.1.10.127.1.1.2.1.3'
                upChannelWidth = self.getSnmpDataNumberSimple(upChannelWidthOid, cm.ip, 'public')
                upTxPowerOid = '1.3.6.1.2.1.10.127.1.2.2.1.3'
                upTxPower = self.getSnmpDataNumberSimple(upTxPowerOid, cm.ip, 'public')
                upRxPowerOid = '1.3.6.1.2.1.10.127.1.3.3.1.6.{}'.format(cm.cmIndex)
                upRxPower = self.getSnmpDataNumberSimple(upRxPowerOid, cm.managerIp, cm.managerCommunity, 5, 1)
                upSignalNoiseOid = '1.3.6.1.2.1.10.127.1.3.3.1.13.{}'.format(cm.cmIndex)
                upSignalNoise = self.getSnmpDataNumberSimple(upSignalNoiseOid, cm.managerIp, cm.managerCommunity, 5, 1)
            except BaseException, msg:
                str = msg
            finally:
                self.cmDataIII.writeResult(cm['ip'],cm['mac'],cm['managerIp'],cm['cmcIndex'],cm['cmIndex'],equalizationData,upChannelId,upChannelFreq,upChannelWidth,upTxPower,upRxPower,upSignalNoise)
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

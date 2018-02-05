from pysnmp.hlapi import *
from pyasn1.type.univ import *
from pysnmp.entity.rfc3413.oneliner import cmdgen

class SnmpUtils:
    def __init__(self, ip , port=161, community='public', timeout = 1, retry = 0):
        self.communityData = CommunityData(community)
        self.udpTransportTarget = UdpTransportTarget((ip,port),timeout,retry)
    def getTable(self,*oids) :
        indexs = []
        variables = {}
        ots = []
        for o in oids:
            ots.append(ObjectIdentity(o[0],o[1]))
        cmd = nextCmd(SnmpEngine(),self.communityData,self.udpTransportTarget,ContextData(),ots)
        while True:
            errorIndication, errorStatus, errorIndex, varBinds = next(cmd)
            if errorIndication:
                raise Exception(errorIndication)
            else:
                if errorStatus:
                    raise Exception('%s at %s\n' % (
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[-1][int(errorIndex)-1] or '?'
                    ))
                else:
                    for varBindTableRow in varBinds:
                        vo = varBindTableRow.__getitem__(0).getOid()
                        val = varBindTableRow.__getitem__(1)
                        status,n,index = getIndex(oids,vo)
                        indexs.append(index)
                        if not status :
                            continue
                        vs = []
                        if variables.has_key(index):
                            vs = variables[index]
                        else:
                            variables[index] = vs
                        vs.insert(n,val)

def getIndex(oids,vo):
    for n,oid in enumerate(oids):
        if oid in vo:
            index = vo.replace(oid,'')
            return True,n,index
    return False,None,None

def val2string(v,isHex):
    if isinstance(v,OctetString):
        if isHex:
            return v.__str__()
        else :
            return v.__bytes__()
    elif isinstance(v,Integer):
        return v.__index__()
    elif isinstance(v,Boolean):
        return v.__index__() == 1
    else:
        return `v`



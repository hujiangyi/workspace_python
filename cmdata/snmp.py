import pprint
from pysnmp.hlapi import *

pp = pprint.PrettyPrinter(indent=4);
ip='172.17.2.162'
oid = '1.3.6.1.2.1.10.127.1.2.2.1.17' 
g = nextCmd(SnmpEngine(),CommunityData('public'),UdpTransportTarget((ip,161)),ContextData(),ObjectType(ObjectIdentity(oid)))
while True:
    a = next(g)
    msg = str(a[0])
    if 'No SNMP response received before timeout' in msg :
        print ip + ' No SNMP response received'
        continue
    nOid = str(a[3][0].__getitem__(0))
    if oid not in nOid :
        break
    value = a[3][0].__getitem__(1)
    pp.pprint(value)
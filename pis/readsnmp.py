import sys
sys.path.append("C:\WINDOWS\SYSTEM32\python27.zip")
sys.path.append("C:\Python27\DLLs")
sys.path.append("C:\Python27\lib")
sys.path.append("C:\Python27\lib\plat-win")
sys.path.append("C:\Python27\lib\lib-tk")
sys.path.append("C:\Python27")
sys.path.append("C:\Python27\lib\site-packages")

from pysnmp.hlapi import *

g = getCmd(SnmpEngine(),CommunityData('public'),UdpTransportTarget(('172.17.2.153',161)),ContextData(),ObjectType(ObjectIdentity('1.3.6.1.4.1.17409.2.3.1.3.1.1.10.1.1')))
a= next(g)
int(a[3][0].__getitem__(1))
from utils.snmp.SnmpUtils import *

snmpUtils = SnmpUtils('172.17.2.148')
indexs1,values1 = snmpUtils.getTable(('IF-MIB', 'ifDescr'),('IF-MIB', 'ifType'))
print indexs1
print values1
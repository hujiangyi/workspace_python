from DatabaseManager import *

dm = DatabaseManager('172.17.1.251','root','ems',3003,'ems')
result = dm.select('select * from pnmpcmdatalast')
for item in result:
    print 'cmMac:{};statusValue:{};checkStatus:{};entityId:{};cmcId:{};tapCoefficient:{};spectrumResponse:{};mtc:{}'.format(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[11],)

data = []
data.append(6)
data.append('00:1C:1D:F6:44:76')
dm.updata("update pnmpcmdatalast set statusvalue=%s where cmmac=%s",data)
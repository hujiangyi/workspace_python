import xlrd
import xlwt
import time

from CollectThread import CollectThread


def run() :
    excel='CM.xls'
    resultExcel='CMresult.xls'
    rb = xlrd.open_workbook(excel)
    wb=xlwt.Workbook()
    sheetCount=len(rb.sheets())
    threads = []
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
            if ip!='' and ip != '0.0.0.0' and 'cmIp' not in ip:
                mac=sheetR.cell(i,2).value
                managerIp=sheetR.cell(i,0).value
                managerCommunity=sheetR.cell(i,1).value
                cmcIndex=sheetR.cell(i,4).value
                cmIndex=sheetR.cell(i,5).value
                print '{} {} {} {} {}'.format(wi,ip,mac,managerIp,managerCommunity)

                while True:
                    for t in threads:
                        if not t.isAlive():
                            print 'end thread:{}'.format(t.ip)
                            threads.remove(t)
                            break
                    if len(threads) < 50:
                        collectThread = CollectThread(ip,mac,managerIp,managerCommunity,cmcIndex,cmIndex,sheetW,wi)
                        collectThread.setDaemon(True)
                        collectThread.start()
                        threads.append(collectThread)
                        break
                    else:
                        time.sleep(1)
                wi += 1
    while True:
        if len(threads) == 0:
            break
        removeThread = []
        for t in threads:
            if not t.isAlive():
                removeThread.append(t)
                break
        for t in removeThread:
            print 'end thread:{}'.format(t.ip)
            threads.remove(t)
    wb.save(resultExcel)

run()
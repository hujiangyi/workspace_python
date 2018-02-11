from threading import *
import time

class TimerThread(Thread):
    def __init__(self,label):
        Thread.__init__(self)
        self.label = label
        self.stop = False
        self.count = 0
    def stop(self):
        self.stop = True
    def run(self):
        while not self.stop:
            tmp = self.count
            hour = tmp / 3600
            tmp = tmp % 3600
            min = tmp / 60
            sec = tmp % 60
            timestr = '{0:0>2}:{1:0>2}:{2:0>2}'.format(hour,min,sec)
            self.label.set(timestr)
            self.count +=1
            time.sleep(1)

#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from Tkinter import *
import tkFont
from xlrd import *
import xlwt
from xlutils.copy import *
from datetime import *
from tkMessageBox import *

from mathgame.utils.TimerThread import TimerThread
from mathgame.DispatchMathType import *

class MathGame:
    def __init__(self,dataPath,targetNumber):
        self.dataPath = dataPath
        self.targetNumber = targetNumber
        self.root = Tk()
        self.initExcel()
        self.initData()
        self.initView()
    def initExcel(self):
        rb = open_workbook(self.dataPath)
        self.wb = copy(rb)
        self.hisScoreSheet = self.wb.get_sheet(0)
        self.currentRoundSheetName = datetime.now().strftime('%Y%m%d%H%M%S')
        self.currentRoundSheet = self.wb.add_sheet(self.currentRoundSheetName)
        self.styleCellRed = xlwt.XFStyle()
        self.currentRoundSheet.write(0, 0, 'subject')
        self.currentRoundSheet.write(0, 1, 'standard result')
        self.currentRoundSheet.write(0, 2, 'your result')
    def initData(self):
        self.firstNum,self.operator,self.secondNum,self.result = dispath()
        self.subjectCount = 1
        self.timerSV = StringVar()
        self.timerSV.set('00:00:00')
        self.totalIV = IntVar()
        self.totalIV.set(0)
        self.rightIV = IntVar()
        self.rightIV.set(0)
        self.wrongIV = IntVar()
        self.wrongIV.set(0)
        self.firstNumIV = IntVar()
        self.operatorSV = StringVar()
        self.secondNumIV = IntVar()
        self.resultSV = StringVar()
        self.firstNumIV.set(self.firstNum)
        self.operatorSV.set(self.operator)
        self.secondNumIV.set(self.secondNum)
    def initView(self):
        helv36 = tkFont.Font(family="Helvetica", size=36)
        Label(self.root, text='计时', font=helv36).grid(row=0, column=0)
        Label(self.root, textvariable=self.timerSV, font=helv36).grid(row=0, column=1, columnspan=5, sticky=W)
        Label(self.root, text='合计', font=helv36).grid(row=0, column=6)
        Label(self.root, textvariable=self.totalIV, width=5, font=helv36).grid(row=0, column=7)
        Label(self.root, textvariable=self.firstNumIV, font=helv36).grid(row=1, column=1, rowspan=2)
        Label(self.root, textvariable=self.operatorSV, font=helv36).grid(row=1, column=2, rowspan=2)
        Label(self.root, textvariable=self.secondNumIV, font=helv36).grid(row=1, column=3, rowspan=2)
        Label(self.root, text='=', font=helv36).grid(row=1, column=4, rowspan=2)
        resultL = Entry(self.root, textvariable=self.resultSV, width=5, font=helv36)
        resultL.grid(row=1, column=5, rowspan=2)
        resultL.focus_set()
        Label(self.root, text='正确', font=helv36).grid(row=1, column=6)
        Label(self.root, textvariable=self.rightIV, width=5, font=helv36).grid(row=1, column=7)
        Label(self.root, text='错误', font=helv36).grid(row=2, column=6)
        Label(self.root, textvariable=self.wrongIV, width=5, font=helv36, fg='red').grid(row=2, column=7)
        Button(self.root, text='看结果').grid(row=3, column=0)
        Button(self.root, text='看历史').grid(row=3, column=1)
        Button(self.root, text='下一题', command=self.nextSubject).grid(row=3, column=7)

        timerThread = TimerThread(self.timerSV)
        timerThread.setDaemon(True)
        timerThread.start()
        self.root.mainloop()
    def nextSubject(self):
        r = self.resultSV.get()
        if r == None or r == '':
            return
        rint = int(r)
        if rint == self.result:
            self.rightIV.set(self.rightIV.get() + 1)
        else :
            self.wrongIV.set(self.wrongIV.get() + 1)
        self.totalIV.set(self.totalIV.get() + 1)
        self.writeSubjectResult(self.firstNum, self.operator, self.secondNum,self.result,r,rint == self.result)
        if self.subjectCount == self.targetNumber :
            self.writeRoundResult(self.currentRoundSheetName,self.totalIV.get(), self.rightIV.get(), self.wrongIV.get(),self.timerSV.get())
            showinfo('info','答题完成')
            self.root.destroy()
            return
        else :
            self.firstNum, self.operator, self.secondNum, self.result = dispath()
            self.subjectCount += 1
            self.firstNumIV.set(self.firstNum)
            self.operatorSV.set(self.operator)
            self.secondNumIV.set(self.secondNum)
            self.resultSV.set('')
    def writeSubjectResult(self,firstNum,operator,secondNum,standard,result,state):
        try :
            self.currentRoundSheet.write(self.subjectCount , 0, '{}{}{}='.format(firstNum,operator,secondNum))
            self.currentRoundSheet.write(self.subjectCount , 1, '{}'.format(standard))
            if not state:
                pattern = xlwt.Pattern()                 # 创建一个模式
                pattern.pattern = xlwt.Pattern.SOLID_PATTERN     # 设置其模式为实型
                pattern.pattern_fore_colour = 2
                self.styleCellRed.pattern = pattern
                self.currentRoundSheet.write(self.subjectCount , 2, '{}'.format(result),self.styleCellRed)
            else :
                self.currentRoundSheet.write(self.subjectCount , 2, '{}'.format(result))
            self.wb.save(self.dataPath)
        except BaseException, msg:
            if 'Permission denied' in msg:
                showinfo('info','请先关闭成绩单，再开始做题！')
                self.root.destroy()
    def writeRoundResult(self,currentRoundSheetName,totalCount,rightCount,wrongCount,useTime):
        row = len(self.hisScoreSheet.get_rows())
        self.hisScoreSheet.write(row, 0, currentRoundSheetName)
        self.hisScoreSheet.write(row, 1, totalCount)
        self.hisScoreSheet.write(row, 2, rightCount)
        self.hisScoreSheet.write(row, 3, wrongCount)
        self.hisScoreSheet.write(row, 4, useTime)
        self.wb.save(self.dataPath)



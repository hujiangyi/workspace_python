#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#

import datetime
import os
import xlrd
from Tkinter import *
from tkFileDialog import *
from tkMessageBox import *
from UpgradeOlt.tools.ModifyUpLink import *
from xlutils.copy import copy
from utils.ListView import *
import pickle
from pnmp.utils import PnmpUtils as utils
import matplotlib.pyplot as pl
import numpy as np



class ShowOneExcel:
    def __init__(self):
        self.root = Tk()
        self.excelPath = StringVar()
        self.row = 0
        self.row = self.rowView(self.row, 'OltExcel', self.excelPath, fun=self.selectExcelPath)
        Button(self.root, text='complte', command=self.closeDialog).grid(row=self.row, column=1)
        self.root.mainloop()
        fig = pl.gcf()
        fig.set_size_inches(10, 8)

    def onClick(self,event):
        index,rowData = self.listView.selectedRowData()
        if rowData == None:
            print "get row data error"
        else:
            freqResult = np.fft.fftfreq(32)
            freqShiftResult = np.fft.fftshift(freqResult)
            ymax = 3.5
            ymin = -3.5
            pl.figure(index)
            mac = rowData["data"][6][1]
            freqResultData = rowData["data"][6][14]
            freqResult = pickle.loads(freqResultData)
            for result in freqResult:
                if result > ymax:
                    ymax = result
                if result < ymin:
                    ymin = result
            lineValue = np.fft.fftshift(freqResult)
            axFreq = pl.subplot(211)
            axAmplitudes = pl.subplot(212)
            amplitudesData = rowData["data"][6][15]
            amplitudes = pickle.loads(amplitudesData)
            amplitudes = utils.toArray24(amplitudes)
            print amplitudes
            pl.sca(axFreq)
            pl.axis([-0.5, 0.5, ymin, ymax])
            pl.grid(True, color="y")
            pl.plot(freqShiftResult, lineValue, 'r', label=mac)
            pl.sca(axAmplitudes)
            barMin = 0
            for v in amplitudes:
                if barMin > v and v != -np.inf:
                    barMin = v
            print np.isfinite(barMin)
            amplitudes = amplitudes - barMin
            pl.xlim(-1, 25)
            pl.bar(np.arange(24), amplitudes, color='r', label=mac, bottom=barMin)
            pl.show()

    def selectExcelPath(self):
        path_ = askopenfilename()
        self.excelPath.set(path_)


    def rowView(self,row,label,textvariable,fun=None,lastLabel='no Label'):
        Label(self.root,text=label).grid(row=row,column=0)
        Entry(self.root,textvariable=textvariable).grid(row=row,column=1)
        if fun != None:
            Button(self.root,text='select',command=fun).grid(row=row,column=2)
        if lastLabel != 'no Label' :
            Label(self.root,text=lastLabel).grid(row=row,column=2)
        row += 1
        return row

    def closeDialog(self):
        if self.excelPath == None or self.excelPath.get() == '':
            showerror('error','The configuration file must be selected')
            return
        self.root.destroy()
        self.showExcel()


    def showExcel(self):
        excelDialog = Tk()
        self.listView = ListView(excelDialog)
        scrbar = Scrollbar(excelDialog)
        self.listView["yscrollcommand"] = scrbar.set
        self.listView.grid(row=0, column=0, columnspan=2)
        cols = [{"key": "managerIp", "width": 300, "text": "managerIp"},
                {"key": "cmcIndex", "width": 100, "text": "cmcIndex"},
                {"key": "ip", "width": 100, "text": "IP"},
                {"key": "mac", "width": 350, "text": "mac"},
                {"key": "cmIndex", "width": 100, "text": "cmIndex"},
                {"key": "upChannelId", "width": 100, "text": "upChannelId"},
                {"key": "data", "width": 100, "text": ""}]
        self.listView.initColumn(cols)
        self.listView.bind("<Double-1>", self.onClick)

        excel = self.excelPath.get()
        rb = xlrd.open_workbook(excel)
        sheetCount = len(rb.sheets())
        for si in range(sheetCount):
            print '%%%%%%%%%%%%%%%%%%%%%%%%%%' + `si` + '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
            sheetR = rb.sheet_by_index(si)
            nrows = sheetR.nrows
            ncols = sheetR.ncols
            for i in range(1, nrows):
                data = []
                for j in range(0, ncols):
                    data.append(sheetR.cell(i, j).value)
                row = {"identifyKey": "ip",
                       "managerIp": data[2],
                       "cmcIndex": data[3],
                       "ip": data[0],
                       "mac": data[1],
                       "cmIndex": data[4],
                       "upChannelId": data[6],
                       "data": data}
                self.listView.insertRow(row)
            excelDialog.mainloop()

ShowOneExcel()
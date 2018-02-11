#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from mathgame.MathGame import MathGame

from Tkinter import *
from mathgame.utils.UiUtils import *

from tkFileDialog import *
from tkMessageBox import *

root = Tk()
excelPathSV = StringVar()
targetNumberIV = IntVar()
targetNumberIV.set(20)
def selectExcelPath():
    path_ = askopenfilename()
    excelPathSV.set(path_)

def closeDialog():
    if excelPathSV == None or excelPathSV.get() == '':
        showerror('error','The database file must be selected')
        return
    root.destroy()
    MathGame(excelPathSV.get(),targetNumberIV.get())

def getValue(globalValue,value):
    re = value
    if value == None or '' == value:
        re = globalValue
    return re
row = 0
row = rowView(root,row,'成绩单',excelPathSV,selectExcelPath)
row = rowView(root,row,'目标个数',targetNumberIV)
Button(root,text='complte',command=closeDialog).grid(row=row,column=1)
root.mainloop()
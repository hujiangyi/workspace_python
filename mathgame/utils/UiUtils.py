#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 jay <hujiangyi@dvt.dvt.com>
#
from Tkinter import *
def rowView(parent,row,label,textvariable,fun=None,lastLabel='no Label'):
    Label(parent,text=label).grid(row=row,column=0)
    Entry(parent,textvariable=textvariable).grid(row=row,column=1)
    if fun != None:
        Button(parent,text='select',command=fun).grid(row=row,column=2)
    if lastLabel != 'no Label' :
        Label(parent,text=lastLabel).grid(row=row,column=2)
    row += 1
    return row
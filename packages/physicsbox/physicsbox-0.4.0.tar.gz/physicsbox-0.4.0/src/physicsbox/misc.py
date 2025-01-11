# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 16:29:34 2021

@author: Leonard.Doyle
"""

from datetime import datetime

def date_now_str():
    dt = datetime.now()
    return dt.strftime('%Y%m%d')

def datetime_now_str():
    dt = datetime.now()
    return dt.strftime('%Y%m%d_%H%M')



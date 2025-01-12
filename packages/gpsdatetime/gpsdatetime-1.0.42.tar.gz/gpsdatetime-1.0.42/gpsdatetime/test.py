#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 19:55:43 2025

@author: beilin
"""
import sys  
sys.path.append("/home/beilin/progs/Prog_scientifique/Packages/gpstime/python/gpsdatetime/gpsdatetime/")
import gpsdatetime as g
import copy

t = g.gpsdatetime()
t2 = copy.copy(t)

print(t)


# t += 56


t2 += 67


x = t2 - t

print(x)
#!/usr/bin/env python 
# -*- coding: utf-8 -*-

''' This is the implementation for 1-D version of Intelligent Driver Model (IDM) 
    Class IDM() is a static class, model for 1-lane driver following behavior.  Metric: SI  
'''
import os 
import sys 
import random 


class IDM(object):
    def __init__(self,v0,a,b, s0 = 2, T = 1.5 ) :
        self.v0, self.delta, self.a, self.b, self.s0,  \
            self.T = v0, DELTA, a, b, s0, T
        
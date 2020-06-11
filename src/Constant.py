import os 
import sys 
 
__author__ = "Haoran Su, Kejian Shi"
__version__ = "1.0.1"

'''
Constants for road environment initilization with SI Metrics
'''

DEBUG = False

ROAD_LEN = 200
MIN_SAFETY_GAP = 1.5  # s_0 
DESIRED_VELOCITY = 15 # v_0  -- free flow speed
SAFE_TIME_HEADWAY = 0.8 # T  default safetime headway for the environment 
COMROT_DECEL_S = 1.8 # b 
COMROT_DECEL_M = 1.6
COMROT_DECEL_L = 1.3
# Most comfortable acceleration is dependent on the type of vehicle (small, medium, or large)






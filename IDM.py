#!/usr/bin/env python 
# -*- coding: utf-8 -*-

''' This is the implementation for 1-D version of Intelligent Driver Model (IDM) 
    Class IDM() is a static class, model for 1-lane driver following behavior.  Metric: SI  
'''
import sys 
import vehicle_env
import math 

__author__ = "Haoran Su, Kejian Shi"
__version__ = "1.0.1"

class Vehicle:
    def __init__(self, acceler = None, speed = None, lane = None, gap = None):
        self.acceler, self.speed, self.lane, self.gap = 4, 10, 0, 3

    def get_desired_velocity(self):
        pass
    def get_safetime_headway(self):
        pass
        
TIME_ELAPSE = 1 
ROAD_LEN = 200 
a_vehicle = Vehicle()

class IDM(object):
    
    def cal_acceler(a_vehicle):
        """
        dv(t)/dt = [1 - (v(t)/v0)^4  - (s*(t)/s(t))^2]
        """
        acceler = math.pow(
            (a_vehicle.velocity / a_vehicle.get_desired_velocity()), 4)
        deceleration = math.pow(IDM.cal_safe_headway(a_vehicle) / a_vehicle.gap, 2)
        return float(a_vehicle.max_acceler * (1 - acceler - deceleration))

    
    def cal_safe_headway(a_vehicle):  
        '''
        cal desired gap
        '''

        pv = a_vehicle.velocity
        if a_vehicle.lead_a_vehicle:
            lpv = a_vehicle.lead_a_vehicle.velocity
        else:
            lpv = pv
        c = ((a_vehicle.get_safetime_headway() * pv) +
             ((pv * (pv - lpv)) / (2 * math.sqrt(
                 a_vehicle.max_acceler * a_vehicle.max_deceleration))))
        res= float(a_vehicle.minimum_distance + max(0, c))
        return res

    
    def cal_velocity(a_vehicle):
        velocity = IDM.cal_raw_velocity(a_vehicle)
        return float(max(0, velocity))

  
    def cal_raw_velocity(a_vehicle):
        return float(a_vehicle.velocity + (IDM.cal_acceler(a_vehicle) *
                                         TIME_ELAPSE))

    def cal_position(a_vehicle):
        if IDM.cal_raw_velocity(a_vehicle) < 0:
            new_position = (a_vehicle.position -
                            (0.5 * (math.pow(a_vehicle.velocity, 2) /
                                    IDM.cal_acceler(a_vehicle))))
        else:
            new_position = (a_vehicle.position +
                            (a_vehicle.velocity * TIME_ELAPSE) +
                            (0.5 * IDM.cal_acceler(a_vehicle) *
                             math.pow(TIME_ELAPSE, 2)))
        return float(new_position)

    def cal_gap(a_vehicle):
        if a_vehicle.lead_a_vehicle:
            return float(a_vehicle.lead_a_vehicle.position -
                         IDM.cal_position(a_vehicle) -
                         a_vehicle.lead_a_vehicle.length)
        else:
            return float(ROAD_LEN + 100)

if __name__ == "__main__":
    pass
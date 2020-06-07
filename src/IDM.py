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


TIME_ELAPSE = 1 
ROAD_LEN = 200 
a_vehicle = Vehicle()

class Vehicle:
    def __init__(self, acceler = None, speed = None, lane = None, gap = None):
        self.acceler, self.speed, self.lane, self.gap = 4, 10, 0, 3
        self.front_vehicle = None

    def get_desired_velocity(self):
        pass
    def get_safetime_headway(self):
        pass
        

class IDM(object):
    
    def cal_acceler(a_vehicle):
        """
        dv(t)/dt = a[1 - (v(t)/v0)^4  - (s*(t)/s(t))^2]
        """
        acceler = math.pow(
            (a_vehicle.velocity / a_vehicle.get_desired_velocity()), 4)
        deceleration = math.pow(IDM.cal_safe_headway(a_vehicle) / a_vehicle.gap, 2)
        return float(a_vehicle.max_acceler * (1 - acceler - deceleration))

    
    def cal_safe_headway(a_vehicle):  
      
        veloc = a_vehicle.velocity
        if a_vehicle.front_vehicle:
            front_veloc = a_vehicle.front_vehicle.velocity
        else:
            front_veloc = veloc
        distance = ((a_vehicle.get_safetime_headway() * veloc) +
             ((veloc * (veloc - front_veloc)) / (2 * math.sqrt(
                 a_vehicle.max_acceler * a_vehicle.max_deceleration))))
        res= float(a_vehicle.minimum_distance + max(0, distance))
        return res

    
    def cal_velocity(a_vehicle):
        velocity = IDM.cal_raw_velocity(a_vehicle)
        return float(max(0, velocity))

  
    def cal_raw_velocity(a_vehicle):
        return float(a_vehicle.velocity + 
                    (IDM.cal_acceler(a_vehicle) *
                                    TIME_ELAPSE))

    def cal_position(a_vehicle):
        if IDM.cal_raw_velocity(a_vehicle) < 0:
            pos_new = (a_vehicle.position -
                        (0.5 * (math.pow(a_vehicle.velocity, 2) /
                        IDM.cal_acceler(a_vehicle))))
        else:
            pos_new = (a_vehicle.position +
                        a_vehicle.velocity * TIME_ELAPSE) +
                        0.5 * IDM.cal_acceler(a_vehicle) *
                        math.pow(TIME_ELAPSE, 2)))
        return float(pos_new)

    def cal_gap(a_vehicle):
        if a_vehicle.front_vehicle:
            return float(a_vehicle.front_vehicle.position -
                         IDM.cal_position(a_vehicle) -
                         a_vehicle.front_vehicle.length)
        else:
            return float(ROAD_LEN + 100)

if __name__ == "__main__":
    pass
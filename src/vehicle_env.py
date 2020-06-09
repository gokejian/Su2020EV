#!/usr/bin/env python 
# -*- coding: utf-8 -*-

''' This is the code for road environment setup with SI metric 
'''
import sys 
import random 
import numpy as np
import math 
import Constant

 
__author__ = "Haoran Su, Kejian Shi"
__version__ = "1.0.1"

class Vehicle(object):
    def __init__(self, length = None):
        # static parameters, for the Intelligent Driver Model 
        self.desired_velocity = Constant.DESIRED_VELOCITY # free_flow_speed 
        self.min_safety_gap = Constant.MIN_SAFETY_GAP # s0 
        self.safe_time_headway = Constant.SAFE_TIME_HEADWAY # T 
        self.length = length
    
        # dynamic attributes 
        self.lead_vehicle = None
        self.velocity = 0 # v, current velocity 
        self.net_distance = 0  # actual gap, calculated by x_i-1 - l_i-1 - x_i, where i-1 is the lead vehicle
        self.lane = 0 # binary: 0 for r, 1 for l 
        self.position = 0 # the head position 
        self.acceleartion = 0 # at t0
        self.desired_acceleration = 0 # updated by the IDM model.  

    def cal_safetime_headway(self):
        ''' ?? What about safetime headway 
        '''
        return 1.5 

    def get_desired_velocity(self): # should be without speed limit 
        return self.desired_velocity

    def set_attributes(self, lead_vehicle,lane, position):
        self.lane = lane # binary: 0 for r, 1 for l 
        self.position = position # the head position 
        self.acceleartion = 0 # at t0
        self.velocity = generate_num_margin_error(8,1)
        # velocity is set d
        if lead_vehicle is not None: 
            self.net_distance = IDM.calc_net_distance(self)
            self.desired_acceleration = IDM.calc_desired_acceler(self) # updated by the IDM model.
            return True 
        else:
            print("!!!!!!!! FIRST VEHICLE !!!!!!!!!")
        
class SmallV(Vehicle):
    def __init__(self):
        super().__init__()
        self.type = 0
        self.length = round(random.uniform (4.00,4.74),2)
        self.max_acceler = 3
        self.comfor_decel = Constant.COMROT_DECEL_S # b
      
class MediumV(Vehicle):
    def __init__(self):
        super().__init__()
        self.type = 1
        self.length = round(random.uniform (4.75,5.34),2)
        self.max_acceler = 3.5
        self.comfor_decel = Constant.COMROT_DECEL_M # b

class LargeV(Vehicle):
    def __init__(self):
        super().__init__()
        self.type = 2
        self.length = round(random.uniform (5.45,6.45),2)
        self.max_acceler = 2
        self.comfor_decel = Constant.COMROT_DECEL_L # b

class IDM():
    @staticmethod
    def calc_net_distance(vehicle):  
        '''net distance
        '''
        if vehicle.lead_vehicle:
            return float(vehicle.lead_vehicle.position - 
                         vehicle.lead_vehicle.length - 
                         vehicle.position)
        else:
            return 0 

    @staticmethod
    def calc_desired_acceler(vehicle):
        """
        dv(t)/dt = a[1 - (v(t)/v0)^4  - (s*(t)/s(t))^2]
        """
        acceleration = math.pow(
            (vehicle.velocity / vehicle.get_desired_velocity()), 4)
        deceleration = math.pow(IDM.calc_desired_gap(vehicle) / vehicle.gap, 2)
        return float(vehicle.max_acceleration * (1 - acceleration - deceleration))

    @staticmethod
    def calc_desired_gap(vehicle):
        # s*
        pv = vehicle.velocity
        if vehicle.lead_vehicle:
            lpv = vehicle.lead_vehicle.velocity
        else:
            lpv = pv # then the velocity difference is 0
        gap = ((vehicle.safe_time_headway * pv) +
             ((pv * (pv - lpv)) / (2 * math.sqrt(
             vehicle.max_acceler * vehicle.comfor_decel)))) 
        '''change max_deceleration to comfor_decel
        '''
        return float(vehicle.min_safety_gap + max(0, gap)) # no negative

def generate_num_margin_error(num, error_range):
    return round(random.uniform (num - error_range , num + error_range),2)
    
def cal_spacing_and_density(curr_density, roadlen, a_vehicle):
    '''get a safe spacing that ensures a "1.5 second rule" given nature of NYC 
    '''
    safe_spacing = Constant.MIN_SAFETY_GAP # braking decleration is about 3-4 times than acceleration
    spacing = safe_spacing + round(random.uniform (0,2.0),1) 
    new_density = curr_density + (spacing + a_vehicle.length) / roadlen
    return spacing , new_density 

class Environment:  
    def __init__(self, density = round(random.uniform (0.1,0.9),1), roadlen = 200):
        self.classes = (SmallV,MediumV,LargeV)
        self.num_smallV = 0
        self.num_mediumV = 0 
        self.num_largeV = 0
        self.density = density 
        self.roadlen = roadlen
        self.cursor = roadlen # start position to fill vehicles 
        self.env_status = [] # keep track of all vehicle information as array of [int:vehicle_index, int:type, int: lane, tuple:center_position, tuple<tuple>: physical_range_at_the_environment, int:speed] 
        
    def get_rand_vehicle(self):
        '''
        # generate a vehicle with chance 1:3:1 being smallV,mediumV,largeV, respectively (reflect NYC traffic)
        '''
        #print("list:" , random.choices(self.classes, weights = [1,2,1]))
        comp_s, comp_m, comp_l = 1, 2, 1
        # by default the composition is 1:2:1 for s,m,l cars
        if len(sys.argv) == 4:
            num_list = []
            for token in sys.argv[3]: 
                if token.isdigit():
                    num_list.append(token)
            comp_s = num_list[0]
            comp_m = num_list[1]
            comp_l = num_list[2]
        a_vehicle = random.choices(self.classes, weights = [comp_s,comp_m,comp_l])[0]() 
        return a_vehicle

    def is_valid(self,curr_density,curr_lane):
        bound_check = (self.cursor > 6)
        if curr_lane == 1:
            bound_check = self.cursor > 194
        return (curr_density < self.density) and bound_check # otherwise cannot fit any car with 4m min len and 2m min gap
    
    def generate_road_env(self):  
        '''
        if rear will exceed the bound, or that it exceed density give it a small vehicle if possible.
        '''
        #[[x_0, y_0, length_0, v_0, acceleration_0= 0, desired_acceleration_0]
        if len(sys.argv) == 3:
            #d esignated density 
            self.density = float(sys.argv[2])
        index_curr_lane = 0 
        lane = 0 # start with right lane
        curr_lane_density = 0
        lead_vehicle = None
        while self.is_valid(curr_lane_density,lane): 
            # print("while loop is running")
            # print("index is ", index )
            a_vehicle = self.get_rand_vehicle()
            spacing , potential_density = cal_spacing_and_density(curr_lane_density,self.roadlen,a_vehicle)
            #(env_density, curr_density, roadlen, a_vehicle):
            bound_check = self.cursor > 6 
            if lane == 1: 
                bound_check = self.cursor > 194
            if (potential_density < self.density) and bound_check:
                # print("enters if (potential_density < self.density) and (self.cursor > 5): ")
                position = round(self.cursor - spacing,2)  # lane is 0 or 1 
                sign_adjust = -1 # if on left lane, then head_val < rear_val. 
                if lane == 1: sign_adjust *= -1
                physical_range = [position, position + (sign_adjust * a_vehicle.length)]
                # [head, rear]

                a_vehicle.set_attributes(lead_vehicle,lane,position)
            

                self.env_status.append([lane, position, a_vehicle.acceleartion, a_vehicle.velocity, IDM.calc_desired_acceler(a_vehicle)])


                if a_vehicle.type == 0:
                    self.num_smallV += 1 
                elif a_vehicle.type == 1:     
                    self.num_mediumV += 1
                elif a_vehicle.type == 2:
                    self.num_largeV += 1
                curr_lane_density = potential_density
                self.cursor = position - a_vehicle.length
                index_curr_lane += 1
            else: 
                # print("enters else")
                if lane == 0: 
                    ''' hit the end of right lane, switch to the left and reset 
                    '''
                    # print("actual right lane density = ", curr_lane_density)
                    lane = 1 
                    index_curr_lane = 0 
                    self.cursor = 0
                    curr_lane_density = 0
                    lead_vehicle = None 
                    continue
                else: 
                    return self.env_status # we can fully stop
        
        return self.env_status  

    def __str__(self):
        print("str called!!")
        # print("Env status: [Small: {}, Medium: {}, Large: {}]".format(self.num_smallV,self.num_mediumV,self.num_largeV))
        # print(" ------------------------------- \n\n", self.env_status, sep = '---') 
    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    num_enviroments = int(sys.argv[1])
    envs = []

    while num_enviroments:
        envs.append(Environment().generate_road_env())
        num_enviroments -= 1
    for a_env in envs:
        print(a_env, '\n\n ================================================== \n')

'''
# [int:vehicle_index, int:type, int: lane, tuple:center_position, tuple<tuple>: physical_range_at_the_environment (), int:speed] 

'''
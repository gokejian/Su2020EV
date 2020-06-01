#!/usr/bin/env python 
# -*- coding: utf-8 -*-

''' This is the code for road environment setup with SI metric 
'''
import os 
import sys 
import random 
import enum
 
__author__ = "Haoran Su, Kejian Shi"
__version__ = "1.0.1"


class SmallV():
    def __init__(self):
        self.id = 0
        self.length = random.randrange(4.00,4.74)
        self.width = random.randrange(1.79,1.86)
        self.max_acceler = random.randrange(3.5,4.5)
        self.speed = 10
        self.center_position = None 

class MediumV():
    def __init__(self):
        self.id = 1
        self.length = random.randrange(4.75,5.44)
        self.width = random.randrange(1.84,1.97)
        self.max_acceler = random.randrange(3.0,6.2)
        self.speed = 10
        self.center_position = None 

class LargeV():
    def __init__(self):
        self.id = 2
        self.length = random.randrange(5.45,6.45)
        self.width = random.randrange(1.94,2.20)
        self.max_acceler = random.randrange(2.0,3.5)
        self.speed = 10
        self.center_position = None 

def generate_num_margin_error(num, error_range):
    return random.randrange(num - error_range , num + error_range)
    
def cal_spacing_and_density(curr_density, roadlen, a_vehicle):
    '''get a safe spacing that ensures a "1.5 second rule" given nature of NYC 
    '''
    safe_spacing = a_vehicle.speed * 1.5 - 0.5 * (a_vehicle.max_acceler * 3) * 1.5^2  # braking decleration is about 3-4 times than acceleration
    spacing = safe_spacing + random.randrange(-0.2,2.0) 

    if spacing < 1:
        spacing = 1
    new_density = curr_density + (spacing + a_vehicle.length) / roadlen
    return spacing , new_density 

class Environment:  
    def __init__(self, density = random.randrange(0.1,0.9), roadlen = 200, roadwid = 10):
        self.classes = (SmallV,MediumV,LargeV)
        self.num_smallV = 0
        self.num_mediumV = 0 
        self.num_largeV = 0
        self.max_speed = 20
        self.density = density 
        self.roadlen = roadlen
        self.roadwid = roadwid
        self.cursor = roadlen # start position to fill vehicles 
        self.env_status = [] # keep track of all vehicle information as array of [int:vehicle_index, int:type, int: lane, tuple:center_position, tuple<tuple>: physical_range_at_the_environment, int:speed] 
        
    '''
    while True:
        try:
        except ValueError:
        print("O")
    '''

    def get_rand_vehicle(self):
        '''
        # generate a vehicle with chance 1:3:1 being smallV,mediumV,largeV, respectively (reflect NYC traffic)
        '''
        a_vehicle = random.choices(self.classes, weights = [1,3,1], k = 1)() 
        return a_vehicle

    '''
    @input road car density 取一个 range: 还是取0-1, 密度按 m/v 计算，让所有值落在0-1区间: normalize 
    @return car index, position, (head_pos,rear_pos) 
    '''

    def is_valid(self,curr_density):
        return (curr_density < self.density) and (self.cursor > 5) # otherwise cannot fit into any car by the 4m car length and 1m of minimum spacing

    def generate_road_env(self):  
        '''
        if rear will exceed the bound, or that it exceed density give it a small vehicle if possible.
        '''
        # [int:vehicle_index, int:type, int: lane, tuple:center_position, tuple<tuple>: physical_range_at_the_environment (), int:speed] 

        # ((self.cursor - 5.74) > 0 ) # here we take a maximum small car with minimum spacing of 1m as a threshold 
        if len(sys.argv == 3):
            ''' designated density 
            '''
            self.density = sys.argv[2]

        HALF_LANE_WID = self.roadwid/4 
        index = 1 
        lane = 0 # 0 or 1 to represent two lanes 
        curr_lane_density = 0
        swith_car_flag = 0
        while self.is_valid(curr_lane_density): 
            a_vehicle = self.get_rand_vehicle()
            spacing , potential_density = cal_spacing_and_density(curr_lane_density,self.roadlen,a_vehicle)
            #(env_density, curr_density, roadlen, a_vehicle):
            if (potential_density < self.density) and (self.cursor > 5):
                rand_width_location = HALF_LANE_WID + random.randrange(-HALF_LANE_WID/2 , + HALF_LANE_WID/2)
                cent_position = (self.cursor - spacing - a_vehicle.length/2 , rand_width_location + lane * self.roadwid/2) # lane is 0 or 1 
                physical_range = ((cent_position - a_vehicle.lenth/2, cent_position + a_vehicle.length/2)
                                 , (cent_position - a_vehicle.width/2, cent_position + a_vehicle.width/2))
                self.env_status.append([index, a_vehicle.id, lane, cent_position, physical_range, a_vehicle.speed])
                if a_vehicle.id == 0:
                    self.num_smallV += 1 
                elif a_vehicle.id == 1:     
                    self.num_mediumV += 1
                elif a_vehicle.id == 2:
                    self.num_largeV += 1
                curr_lane_density = potential_density
                self.cursor = cent_position - a_vehicle.length/2
                index += 1
            else: 
                if lane == 0:
                    print("actual right lane density = ", curr_lane_density)
                    lane = 1 
                    self.cursor = self.roadlen
                    curr_lane_density = 0
                    continue
        
        return self.env_status  

    def __repr__(self):
        print("Env status: [Small: {}, Medium: {}, Large: {}]".format(self.num_smallV,self.num_mediumV,self.num_largeV))
        print(" ------------------------------- \n\n", self.env_status, sep = '---') 
    

if __name__ == "__main__":
    num_enviroments = sys.argv[1]
    envs = []
    while num_enviroments:
        envs.append(Environment().generate_road_env())
        num_enviroments -= 1
    for a_env in envs:
        print(a_env,sep = ' \n ========================================== \n')

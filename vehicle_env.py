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


#'{} {}'. format(self.first, self. last) 


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
    
def cal_spacing_and_density(env_density, curr_density, roadlen, a_vehicle):
    '''get a safe spacing that ensures a "1.5 second rule" given nature of NYC 
    '''
    safe_spacing = a_vehicle.speed * 1.5 - 0.5 * (a_vehicle.max_acceler * 3) * 1.5^2  # braking decleration is about 3-4 times than acceleration
    spacing = safe_spacing + random.randrange(-0.2,2.0) 

    if spacing < 1:
        spacing = 1
    new_density = curr_density + (spacing + a_vehicle.length) / roadlen
    return spacing , new_density 

class Environment:  
    '''
    each car, index,length,physical range on the road, acceleration, env里分别有多少大中小车 (total不需单独出))  
    需要 每辆车的center position, 关键还需要验证是不是合理（out_of_bounds），通过那个和长度算出 head 和 rear (stretch)
    '''
    def __init__(self, roadlen = 200, roadwid = 10, density = random.randrange(0.1,0.9)):
        self.classes = (SmallV,MediumV,LargeV)
        self.num_smallV = 0
        self.num_mediumV = 0 
        self.num_largeV = 0
        self.max_speed = 20
        self.density = density 
        self.roadlen = roadlen
        self.roadwid = roadwid
        self.cur_cursor = roadlen # start position to fill vehicles 
        self.env_status = [] # keep track of all vehicle information as array of [int:vehicle_index, int:type, int: lane, tuple:center_position, tuple<tuple>: physical_range_at_the_environment, int:speed] 
        
    '''
    while True:
        try:
        x = int(input("Please enter a number: "))
        except ValueError:
        print("Oops!  That was no valid number.  Try again...")

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

    def is_valid(self):
        return (self.curr_density < self.density) and (self.cur_cursor > 5) # otherwise cannot fit into any car by the 4m car length and 1m of minimum spacing

    def generate_road_env(self):  
        '''
        1. while not less than minimum length requirement (with min of 1m spacing) get a car # The pre-checking is tough. 
        2. generate_car and set a flag 
        3. calculate spacing needed
        3。check if rear will exceed the bound, or that it exceed density 
        4. if not then put the car. with center position being half length + center of uni lane with small margin of error. 
        update the env_status by append. and update the class variable 
        5. if so, give it a small vehicle if possible. Use break and continue wisely 
        6. switch another lane, repeat the process 
        '''
        # [int:vehicle_index, int:type, int: lane, tuple:center_position, tuple<tuple>: physical_range_at_the_environment (), int:speed] 

        # ((self.cur_cursor - 5.74) > 0 ) # here we take a maximum small car with minimum spacing of 1m as a threshold 
        HALF_LANE_WID = self.roadwid/4 
        index = 1 
        lane = 0  
        curr_lane_density = 0
        physical_range = ()
        succeed_flag = 0
        while self.is_valid(): 
            a_vehicle = get_rand_vehicle()
            spacing , potential_density = cal_spacing_and_density(self.density,curr_lane_density,self.roadlen,a_vehicle)
            #(env_density, curr_density, roadlen, a_vehicle):
             if (potential_density < curr_lane_density) and (self.cur_cursor

            




    def __repr__(self):
        pass 


if __name__ == "__main__":
    pass

    '''
    from random import choice
classes = (RoomSpider, RoomSoldier, RoomDragon, ...)
room = [[choice(classes)() for _ in range(2)] for __ in range(2)]

   grid = [[1]*8 for i in range(8)]
   for row in grid:
       for column in row:
           da
    '''

        '''
        肯定是，density 过了， 或次小的车已经放不下了

 if a_vehicle.id == 0:
            self.num_smallV += 1 
        elif a_vehicle.id == 1:     
            self.num_mediumV += 1
        elif a_vehicle.id == 2:
            self.num_largeV += 1

        ''''
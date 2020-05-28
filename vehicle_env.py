#!/usr/bin/env python 
# -*- coding: utf-8 -*-


''' This is the code for road environment setup 
'''
import os 
import sys 
import random 
import enum
 
__author__ = "Haoran Su, Kejian Shi"
__version__ = "1.0.1"

'''
To do: 

acceleration 放到case里直接写

format 这样写： '{} {}'. format(self.first, self. last) 

def repr 

value: random.randint(1,6) // inclusive 
list = ['R','G','B']
.choice(list) Can be list of classes 
.choices(list, weights = [3,3,1] k = 4) //要4个 , 则3:3:1的形式rand 4个

Velocity: an action following the resulting policy from DDPG neural network

问题：

'''

class Timestamp: 
    '''
    10 - 30 seconds per instruction, but we need acclelration
    '''
    pass 
    def get_time(self):
        pass 

class Vehicle: 
    def __init__(self, speed, length, max_acceler):
        self.length = length 
        self.speed = speed
        self.max_acceler = max_acceler

''' 
metric: SI 

'''
class SmallV(Vehicle):
    def __init__(self, speed):
        self.id = 0
        self.length = random.randrange(4.10,4.74)
        self. width = random.randrange(1.79,1.86)
        self.max_acceler = random.randrange(2.0,3.0)

class MediumV(Vehicle):
    def __init__(self, speed):
        self.id = 1
        self.length = random.randrange(4.75,5.44)
        self.width = random.randrange(1.84,1.97)
        self.max_acceler = random.randrange(2.5,6.5)

class LargeV(Vehicle):
    def __init__(self, speed):
        self.id = 2
        self.length = random.randrange(5.45,6.45)
        self.width = random.randrange(1.94,2.20)
        self.max_acceler = random.randrange(2.0,4.0)

class Environment:  
    '''
    each car, index,length,physical range on the road, acceleration, env里分别有多少大中小车 (total不需单独出))  
    需要 每辆车的center position, 关键还需要验证是不是合理（重叠，out_of_bounds），通过那个和长度算出 head 和 rear

    最后的density 是按照面积除以总面积做？

    这块要想想：
    center position 其实可以放进Car. ASSIGN 是在Env里通过计算然后给他的

    distribution 问题： 考不考虑 像density = 0.5, 是全部分散开0.5呢，还是一边全挤在一起， 怎么去tune这个条件

    第二阶段: 旁边是什么车 (later)
    '''
    def __init__(self, roadlen = 200, roadwid = 10, density = random.randrange(0.1,0.9)):
        self.num_smallV = 0
        self.num_mediumV = 0 
        self.num_largeV = 0
        self.density = density
        self.roadlen = roadlen
        self.roadwid = roadwid
        self.classes = (SmallV,MediumV,LargeV)
        self.vehicles = [] 
    
    def valid(self):
        pass 

    def get_rand_vehicle(self):
        a_vehicle = random.choice(self.classes)()
        if a_vehicle.id == 0:
            self.num_smallV += 1 
        elif a_vehicle.id == 1:     
            self.num_mediumV += 1
        elif a_vehicle.id == 2:
            self.num_largeV += 1

    '''
    @input road car density 取一个 range: 还是取0-1, 密度按 m/v 计算，让所有值落在0-1区间: normalize 
    @return car index, position, (head_pos,rear_pos) 
    '''

    def is_valid(self):
        pass

    def generate_road_env(self):  
        while self.is_valid():
            print(1)
    '''
    需要根据density 的设置，产生random生产的上限
    '''
    def __repr__(self):
        pass 


if __name__ == "__main__":
    pass

    '''
    from random import choice
classes = (RoomSpider, RoomSoldier, RoomDragon, ...)
room = [[choice(classes)() for _ in range(2)] for __ in range(2)]
    '''
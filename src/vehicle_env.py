#!/usr/bin/env python 
# -*- coding: utf-8 -*-

''' This is the code for road environment setup with SI metric 
'''
import sys 
import os
import shutil
import random 
import numpy as np
import math
import sys, os
sys.path.append('')
import Constant

 
__author__ = "Haoran Su, Kejian Shi"
__version__ = "1.0.2"


ratio_list = [1,2,1] # default 1,2,1; updated by command line arguments

class Vehicle(object):
    def __init__(self, length = None):
        # static parameters, for the Intelligent Driver Model 
        self.desired_velocity = Constant.DESIRED_VELOCITY # free_flow_speed 
        self.min_safety_gap = Constant.MIN_SAFETY_GAP # s0 
        self.safe_time_headway = Constant.SAFE_TIME_HEADWAY # T 
        self.length = length
        self.index_curr_lane = 0 # give a numerical order of the car
    
        # dynamic attributes 
        self.lead_vehicle = None
        self.velocity = 0 # v, current velocity 
        self.net_distance = 10 # default non-zero actual gap 
        self.lane = 0 # binary: 0 for r, 1 for l 
        self.position = 0 # the head position 
        self.acceleartion = 0 # at t0
        self.desired_acceleration = 0 # updated by the IDM model.  
        self.action_indicator = 0 # whether "yield" was executed
    
 
    def cal_safetime_headway(self):
        ''' ?? What about safetime headway 
        '''
        return Constant.SAFE_TIME_HEADWAY 

    def get_desired_velocity(self): # should be without speed limit 
        return self.desired_velocity

    def has_lead_vehicle(self):
        return self.lead_vehicle is not None


    def set_attributes(self, lead_vehicle,lane, position,index_curr_lane):
        # print("After entering set attributes, lead_vehicle is:{}",format(lead_vehicle)) 
        self.lane = lane # binary: 0 for r, 1 for l 
        self.position = position # the head position 
        self.acceleartion = 0 # at t0
        self.velocity = 7 # set all initial speed to 7 
        # velocity is set d
        self.lead_vehicle = lead_vehicle
        self.index_curr_lane = index_curr_lane
        if self.lead_vehicle is not None: 
            #print("!!! ENTERS set_attribute.(lead_vehicle is not None)!!!!!!\n\n")
            self.net_distance = IDM.calc_net_distance(self)
            self.desired_acceleration = IDM.calc_desired_acceler(self) # updated by the IDM model.
            return True 
        else:
            # print(self.lead_vehicle, "    ", self.net_distance, "    ", self.desired_acceleration, " \n" )
            return False # meaning that this is the leading car in the lane
        
class SmallV(Vehicle):
    def __init__(self):
        super().__init__()
        self.type = 0
        self.length = round(random.uniform (4.00,4.74),2)
        self.max_acceler = 1
        self.comfor_decel = Constant.COMROT_DECEL_S # b
      
class MediumV(Vehicle):
    def __init__(self):
        super().__init__()
        self.type = 1
        self.length = round(random.uniform (4.75,5.34),2)
        self.max_acceler = 1.3
        self.comfor_decel = Constant.COMROT_DECEL_M # b

class LargeV(Vehicle):
    def __init__(self):
        super().__init__()
        self.type = 2
        self.length = round(random.uniform (5.45,6.45),2)
        self.max_acceler = 0.75
        self.comfor_decel = Constant.COMROT_DECEL_L # b
 
class IDM():
    @staticmethod
    def calc_net_distance(vehicle):  
        '''net distance x_i-1 - l_i-1 - x_i, where i-1 is the length of the lead vehicle 
        '''
       # print("!!! ENTERS IDM.calc_net_distance!!!!!!\n\n")
       # print("======what happend here?: vehicle: \n" , vehicle ,"\n vehicle.lead_vehicle: \n", vehicle.lead_vehicle, "\n\n") 
        if(vehicle.lane == 1):
            return round(float(vehicle.position - 
                        vehicle.lead_vehicle.length -
                        vehicle.lead_vehicle.position),2)
        
        return round(float(vehicle.lead_vehicle.position - 
                        vehicle.lead_vehicle.length - 
                        vehicle.position),2)
    
    @staticmethod
    def calc_desired_acceler(vehicle):
        """
        dv(t)/dt = a[1 - (v(t)/v0)^4  - (s*(t)/s(t))^2]
        """
        acceleration = math.pow(
            (vehicle.velocity / vehicle.get_desired_velocity()), 4)
        deceleration = math.pow(IDM.calc_desired_gap(vehicle) / vehicle.net_distance, 2)
        # note here vehicle.net_distance should be non-zero. Default set to 5

        return round(float(vehicle.max_acceler * (1 - acceleration - deceleration)),2)

    @staticmethod
    def calc_desired_gap(vehicle): 
        ''' s*
        '''
        pv = vehicle.velocity
        if vehicle.lead_vehicle is not None:
            lpv = vehicle.lead_vehicle.velocity
        else:
            print("<<<<<<<In cal_desired_gap>>>>>>>" )
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
    safe_spacing = Constant.MIN_SAFETY_GAP   
    spacing = safe_spacing + round(random.uniform (1,3.0),1) 
    # print("The car length is: <<" , a_vehicle.length, ">>\n")
    new_density = curr_density + (spacing + a_vehicle.length) / roadlen
    return spacing , new_density 
 
class Environment:  
    def __init__(self, roadlen = 100):
        self.classes = (SmallV,MediumV,LargeV)
        self.num_left = 0
        self.num_right = 0 
        self.num_smallV = 0
        self.num_mediumV = 0 
        self.num_largeV = 0
        self.num_v = self.num_largeV + self.num_mediumV + self.num_smallV
        self.density = round(random.uniform (0.2,0.9),1)
        self.roadlen = roadlen
        self.cursor = roadlen # start position to fill vehicles 
        self.env_status = [] # keep track of all vehicle information as array of [int:vehicle_index, int:type, int: lane, tuple:center_position, tuple<tuple>: physical_range_at_the_environment, int:speed] 
        
    def get_rand_vehicle(self):
        '''
        # generate a vehicle with chance 1:3:1 being smallV,mediumV,largeV, respectively (reflect NYC traffic)
        '''
        #print("list:" , random.choices(self.classes, weights = [1,2,1])) 
        a_vehicle = random.choices(self.classes, weights = [ratio_list[0],
                                    ratio_list[1],ratio_list[2]])[0]() 
        return a_vehicle

    def is_valid(self,curr_density,curr_lane):
        bound_check = (self.cursor > 6)
        if curr_lane == 1:
            bound_check = self.cursor < 94
        return (curr_density < self.density) and bound_check # otherwise cannot fit any car with 4m min len and 2m min gap
    
    def generate_road_env(self):  
        '''
        if rear will exceed the bound, or that it exceed density give it a small vehicle if possible.
        '''
        #[[x_0, y_0, length_0, v_0, desired_acceleration_0]
        if len(sys.argv) >= 3:
            # designated density 
            self.density = float(sys.argv[2])
        index_curr_lane = 0 
        lane = 0 # start with right lane
        curr_lane_density = 0
        lead_vehicle = None
        while self.is_valid(curr_lane_density,lane): 
          #  print("=======while loop is running=======", index_curr_lane)
            # print("index is ", index )
            a_vehicle = self.get_rand_vehicle()
          #  print("lead_vehicle is: <<<<<" ,lead_vehicle ," >>>>>>>")

            spacing , potential_density = cal_spacing_and_density(curr_lane_density,self.roadlen,a_vehicle)
            #(env_density, curr_density, roadlen, a_vehicle):
            bound_check = self.cursor > 6 
            if lane == 1: 
                bound_check = self.cursor < 94
            if (potential_density < self.density) and bound_check:
                # print("enters if (potential_density < self.density) and (self.cursor > 5): ")
                ''' 
                modify the position calculation technique 
                '''
                sign_adjust = 1
                indicator = 0
                if lane == 1: 
                    sign_adjust = -1
                    indicator = 1

                position = round(self.cursor + sign_adjust * (-1) * spacing + indicator * a_vehicle.length,2)  
                # [head, rear]

               # print("AT LINE 196, the lead_vehicle updated?: ", lead_vehicle)
               
                a_vehicle.set_attributes(lead_vehicle,lane,position,index_curr_lane)

                if Constant.DEBUG:
                    print("====== NOW TESTING THE ARITHMETICS ====== \n The car on lane <{}> \n The car has <{}> lead_vehicle  \n"
                                        "The car has position <{}>,\n" 
                                        "The spacing is <{}>,\n The net_distance is <{}>,\n it has length <{}>\
                                            ".format(a_vehicle.lane,a_vehicle.has_lead_vehicle(),a_vehicle.position,spacing,
                                                    a_vehicle.net_distance,a_vehicle.length))

                self.env_status.append([position,lane,a_vehicle.velocity,
                                        a_vehicle.length, a_vehicle.comfor_decel, a_vehicle.action_indicator])
                #print(self.env_status, '\n\n\n')
                if a_vehicle.type == 0:
                    self.num_smallV += 1 
                elif a_vehicle.type == 1:     
                    self.num_mediumV += 1
                elif a_vehicle.type == 2:
                    self.num_largeV += 1
                    
                curr_lane_density = potential_density

                if lane == 0: 
                    self.cursor = position - a_vehicle.length 
                else: 
                    self.cursor = position
                # cursor always points to the rear of the vehicle 

                index_curr_lane += 1
                lead_vehicle = a_vehicle
                #print("lead_vehicle is: <<<<<" ,lead_vehicle ," >>>>>>>")
            else: 
                # print("enters else")
                if lane == 0: 
                    ''' hit the end of right lane, switch to the left and reset 
                    '''
                    # print("actual right lane density = ", curr_lane_density)
                    lane = 1 
                    self.num_right = index_curr_lane + 1
                    index_curr_lane = 0 
                    self.cursor = 0
                    curr_lane_density = 0
                    lead_vehicle = None 
                    continue
                else: 
                    self.num_left = index_curr_lane + 1
                    return self.env_status # we can fully stop
        
        return self.env_status  

    def __str__(self):
        print("str called!!")
        # print("Env status: [Small: {}, Medium: {}, Large: {}]".format(self.num_smallV,self.num_mediumV,self.num_largeV))
        # print(" ------------------------------- \n\n", self.env_status, sep = '---') 
    def __repr__(self):
        return self.__str__()

def generate_env_nparray(num = 10): #default env is 10  
    np.set_printoptions(suppress=True)
    envs_lst = []
    while num:
        raw_env = Environment()
        # print(raw_env.density)
        a_env = raw_env.generate_road_env()
        envs_lst.append(a_env)
        num -= 1
    return envs_lst

def main():
    if len(sys.argv) == 4:
        indx = 0
        for token in sys.argv[3]: 
            if token.isdigit():
                ratio_list[indx] = int(token)
                indx += 1
                    
    np.set_printoptions(suppress=True)
    envs = []
    num_enviroments = int(sys.argv[1])
    store_num_env = num_enviroments 

    os.chdir("/Users/markshi/Documents/GitHub/research_projects/NYU/Su2020EV/outputs")  # need to mofify the working directory here 

    folder = os.getcwd()
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    log = open("log.txt","w+")
    log.write("Total of %d env(s) generated\r\n " % (store_num_env))

    while num_enviroments:
        raw_env = Environment()
        a_env = raw_env.generate_road_env()
        np_env = np.array(a_env)
        indx = store_num_env - num_enviroments         
        sys.stdout = open(os.getcwd() + "/env_ %i .txt" % (indx),'w')
        print(np_env)
        log.write("Env <%d> has: \r %d small cars, \r %d medium cars, \r %d large cars. \n\r" % (indx, raw_env.num_smallV,
                                    raw_env.num_mediumV, raw_env.num_largeV))
        envs.append(a_env)
        num_enviroments -= 1   
    return envs

if __name__ == "__main__":
    main()
 
    


'''
# [int:vehicle_index, int:type, int: lane, tuple:center_position, tuple<tuple>: physical_range_at_the_environment (), int:speed] 

'''
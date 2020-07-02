# -*- coding: utf-8 -*-
"""Author: Haoran Su
Email: hs1854@nyu.edu
"""
import numpy as np
# action is encoded as a 15-bits binary number


# Encode action from a list of integers(binary) into a string
def encode_action(b_action):
    string_res = ''
    for elem in b_action:
        string_res += str(elem)
    return string_res


# Decode a string action into a list of integers, which are actions for each vehicle
def decode_action(s_action):
    res = []
    str_list = f'{s_action:015b}'.split()
    for char in str_list[0]:
        res.append(int(char))
    return res


# Global parameters
L = 200  # Length of the roadway segment
l_gap = 0.2  # Minimum safety gap
delta_t = 0.25  # length of the timestamp interval

"""A vehicle feature vector should be described as:
[x, y, v, l, b*, status].
Where status indicated as:
0: continue trip;
1: pull-over, stop depends on lane position
2: nullified, just for state mapping"""


def mapped_state(state):
    """
    Mapped a given state into the state as neural network input, insert trivial vehicles until vehs_num = 15
    :param state: given state
    :return: new state
    """
    num_diff = 10 - len(state)
    for i in range(num_diff):
        # status of which vehicle is 2, indicating this vehicle is trivial
        state.append([0, 0, 0, 0, 0, 2])

    return state


def random_deceleration(most_comfortable_deceleration, lane_pos):
    """
    Return a deceleration based on given attribute of the vehicle
    :param most_comfortable_deceleration: the given attribute of the vehicle
    :param lane_pos: y
    :return: the deceleration adopted by human driver
    """
    if lane_pos:
        sigma = 0.2
    else:
        sigma = 0.3
    return np.random.normal(most_comfortable_deceleration, sigma)


# Calculating rewards depends only on the state:
def calculate_reward(observation_):
    """
    Calculate reward for the given state. Notice that this function doesnt account for status inconsistency, but it gets
    covered in the state_transition function.
    :param vehs:
    :return: reward, a scalar for this state
    """
    num_vehicles = len(observation_)  # num_vehs = 15
    # Initialize reward
    reward = 0
    # For the new state:
    # First, we want to check collision:
    for i in range(num_vehicles):
        for j in range(i+1, num_vehicles):
            # Front pos of veh i:
            front_pos = observation_[i][0]
            # Back pos of veh j:
            back_pos = observation_[j][0] - observation_[j][3]
            # Collision check: 1. both vehicles are not trivial, 2. both vehicles are on the same lane.
            # 3: two vehicles have overlapped.
            if observation_[i][1] == observation_[j][1] and observation_[i][5] != 2 and observation_[j][5] != 2 and \
                    (front_pos + l_gap) > back_pos:
                reward -= 1000
    # If any vehicle is on lane 0 and vehicle position has not exceed the roadway length:
    for veh in observation_:
        if (veh[5] != 2) and (veh[1] == 0) and (veh[0] - veh[3] <= L):
            reward -= 1

    return reward


def step(observation, s_action):
    """
    State Transition function to compute the next state
    :param vehs: old state, i.e. vehs
    :param action: action associated
    :return: observation_,(next_state) reward, done(whether the process has completed)
    """
    action = decode_action(s_action)
    # Initialize next state
    observation_ = []
    num_vehs = len(observation)

    # Initialize a status inconsistency counter:
    status_inconsistency = 0

    for i in range(num_vehs):
        action_i = action[i]
        new_x = observation[i][0] + observation[i][2] * delta_t
        # Generate the actual deceleration adopted by human driver:
        b_actual = random_deceleration(observation[i][4], observation[i][1])
        # Velocity cannot be negative
        new_v = max(0, observation[i][2] - b_actual * delta_t)
        # New position for vehicles who pulled over
        new_y = (observation[i][1] == 0) and (new_v == 0) and (action_i == 1)

        old_status = observation[i][5]
        # New status will follow the action value, but a vehicle' status cannot be from 1 to 0
        new_status = action[i]

        if old_status and (new_status == 0):
            # Record the status inconsistency
            status_inconsistency += 1

        new_veh = [new_x, new_y, new_v, observation[i][3], observation[i][4], new_status]
        observation_.append(new_veh)

    # Calculate reward
    reward = calculate_reward(observation_)
    # If there is any inconsistency in the status, we gives additional penalty
    if status_inconsistency >= 0:
        reward -= 1000

    # Check if the process has completed by examine no vehicles are on lane 0 in the new state:
    flag = False
    for veh in observation_:
        if (veh[5] != 2) and (veh[2] == 0) and (veh[0] - veh[3] < L):
            flag = True

    if flag:
        done = False
    else:
        done = True
    return observation_, reward, done
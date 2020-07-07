# -*- coding: utf-8 -*-
"""Author: Haoran Su
Email: hs1854@nyu.edu
"""
import vehicle_env
import numpy as np

# Action is now defined that index of vehicle start to yield at given step
# Under this scheme, only one vehicle can yield at each step
# action = -1 if no vehicle is yielding at the end of this step

# # Utility function
# def decode_action(s_action):
#     res = []
#     str_list = f'{s_action:015b}'.split()
#     for char in str_list[0]:
#         res.append(int(char))
#     return res


def mapped_state(state):
    """
    Mapped a given state into the state as neural network input, insert trivial vehicles until vehs_num = 15
    :param state: given state
    :return: new state
    """
    num_diff = 15 - len(state)
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
        sigma = 0.3
    else:
        sigma = 0.5
    return np.random.normal(most_comfortable_deceleration, sigma)


# Calculating rewards depends only on the state:
def calculate_reward(state, l_gap=0.5, road_length=100):
    """
    Calculate reward for the given state. Notice that this function doesnt account for status inconsistency, but it gets
    covered in the state_transition function.
    :param road_length: segment length
    :param l_gap: minimum safety gap
    :param state: given state
    :return: reward for this state
    """
    num_vehs = len(state)
    # Initialize reward
    reward = 0

    # Initialize collision indicator:
    has_collision = False

    # Initialize path cleared indicator:
    has_cleared = True

    # For the new state:
    # First, we want to check collision:
    for i in range(num_vehs):
        for j in range(i + 1, num_vehs):

            # Determine which vehicle is the leading vehicle by their front position:
            if state[i][0] >= state[j][0]:
                leading_veh = state[i]
                following_veh = state[j]
            else:
                leading_veh = state[j]
                following_veh = state[i]

            # Find out the back of leading vehicle and front of following vehicle:
            back_pos = leading_veh[0] - leading_veh[3]
            front_pos = following_veh[0]

            # Collision check: 1. both vehicles are on the same lane, 2: two vehicles have overlapped with minimum
            # safety gap.
            if leading_veh[1] == following_veh[1] and back_pos - l_gap < back_pos:
                has_collision = True

    # If any vehicle is on lane 0 and vehicle position has not exceed the roadway length:
    for veh in state:
        if veh[1] == 0 and veh[0] - veh[3] <= road_length:
            has_cleared = False

    # Summarize reward:
    if has_collision:
        reward -= 10

    if not has_cleared:
        reward -= 1
    else:
        reward += 10

    return has_cleared, reward


# Road Environment
class RoadEnv:
    def __init__(self, road_length=100, l_gap=0.2, delta_t=0.25):
        self.state = mapped_state(vehicle_env.generate_env_nparray())
        self.done = False
        self.road_length = road_length  # Length of the roadway segment
        self.l_gap = l_gap  # Minimum safety gap
        self.delta_t = delta_t  # length of the timestamp interval
        print("number of vehicles is : "+str(len(self.state)))

    def reset(self):
        new_state = vehicle_env.generate_env_nparray()
        print("number of vehicles is : "+str(len(self.state)))
        self.state = mapped_state(new_state)
        return self.state

    def step(self, observation, action):
        """
            State Transition function to compute the next state
            :param s_action: integer action
            :param observation: s(t)
            :return: observation_,(next_state) reward, done(whether the process has completed)
            """

        # action = decode_action(s_action)
        # Initialize next state
        observation_ = []

        # Initialize a status inconsistency counter:
        status_inconsistency = False

        # Find the number of valid vehicles and only iterate through valid vehicles
        num_valid_vehs = 0
        for veh in observation:
            if veh[5] != 2:
                num_valid_vehs += 1

        for i in range(num_valid_vehs):

            # # extract corresponding action
            if action == i:
                action_i = 1
            else:
                action_i = 0

            # Model vehicle kinetics here:

            # new_x = old_x + old_velocity * step
            new_x = observation[i][0] + observation[i][2] * self.delta_t

            # If the action for this vehicle is to yield:
            if action_i:
                # new_b = generate a new deceleration based on vehicle most comfortable deceleration
                b_actual = random_deceleration(observation[i][4], observation[i][1])
            # if this is not the vehicle which needs to yield:
            else:
                b_actual = 0

            # new_v: max(0, old_velocity - old_b * step)
            new_v = max(0, observation[i][2] - b_actual * self.delta_t)

            # new_y: if old_y = 0, new_v = 0 and action = 1, assign new lane position
            # NOTICE: lane changing(pull over) happens at the end of each step
            if (observation[i][1] == 0) and (new_v == 0) and (action_i == 1):
                new_y = 1
            else:
                # No lane changing happened at this step:
                new_y = observation[i][1] == 0

            # New status will follow the action value, but a vehicle' status cannot be from 1 to 0
            new_status = action_i
            if observation[i][5] and (new_status == 0):
                # Record the status inconsistency
                status_inconsistency = True

            # Assign new vehicle information and add it to the new observation
            new_veh = [new_x, int(new_y), new_v, observation[i][3], observation[i][4], new_status]
            observation_.append(new_veh)

        # Calculate reward without considering action-status inconsistency
        # At this step, observation_ only contains valid vehicles, and reward is only calculated for that:
        # Check if the process also completes in this step:
        done, reward = calculate_reward(observation_, road_length=self.road_length, l_gap=self.l_gap)

        # Additionally, if there is any inconsistency in the status, we applies penalty:
        if status_inconsistency:
            reward -= 10

        # Map the next state to consistent state length:
        observation_ = mapped_state(observation_)

        return observation_, reward, done
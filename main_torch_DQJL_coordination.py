# -*- coding: utf-8 -*-
"""Author: Haoran Su
Email: hs1854@nyu.edu
"""
from DQN_Agent import VehicleNet, Agent
from utils import plotLearning
import numpy as np

# Global parameters
L = 200  # Length of the roadway segment
l_gap = 2  # Minimum safety gap
delta_t = 0.5  # length of the timestamp interval


""" Each vehicle is described as veh = [x, y, v, l, b*, status]
"""

"""
Vehicle: state of the vehicle
"""

def calculate_reward(observation_, obeservation, action):
    """
    Calculate reward for the given state
    :param vehs:
    :return: reward, a scalar for this state
    """
    num_vehicles = len(observation_)
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
            if front_pos + l_gap > back_pos and observation_[i][1] == observation_[j][1]:
                reward -= 1000
    # If any vehicle is on lane 0 and vehicle position has not exceed the roadway length:
    for veh in observation_:
        if (veh[1] == 0) and (veh[0] - veh[3] <= L):
            reward -= 1

    # For the old state:
    # Force the vehicle continue to yield if he is instructed to do so:
    for i in range(len(observation)):
        if observation[i] == 1 and action[i] != 1:
            reward -= 1000

    return reward


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
        sigma = 0.4
    return np.random.normal(most_comfortable_deceleration, sigma)


def step(observation, action):
    """
    State Transition function to compute the next state
    :param vehs: old state, i.e. vehs
    :param action: action associated
    :return: observation_,(next_state) reward, done(whether the process has completed)
    """

    assert(len(observation) == len(action))
    observation_ = []
    num_vehs = len(observation)

    for i in range(num_vehs):
        action_i = action[i]
        new_x = observation[i][0] + observation[i][2] * delta_t
        # Generate the actual deceleration adopted by human driver:
        b_actual = random_deceleration(observation[i][4], observation[i][1])
        # Velocity cannot be negative
        new_v = max(0, observation[i][2] + b_actual * delta_t)
        # New position for vehicles who pulled over
        new_y = (observation[i][1] == 0) and (new_v == 0) and (action_i == 1)

        # If the status of the vehicle indicating not yielding, but the action is to yield, update status:
        if (observation[i][5] == 0) and action[i]:
            new_status = 1
        else:
            new_status = 0

        new_veh = [new_x, new_y, new_v, observation[i][3], observation[i][4], new_status]
        observation_.append(new_veh)

    # Calculate reward
    reward = calculate_reward(observation_, observation, action)

    # Check if the process has completed by examine no vehicles are on lane 0 in the new state:
    flag = False
    for veh in observation_:
        if veh[2] == 0 and (veh[0] - veh[3] < L):
            flag = True

    if flag:
        done = False
    else:
        done = True
    return observation_, reward, done


# Main:
if __name__ == '__main__':
    agent = Agent(gamma=0.99, epsilon=1.0, batch_size=64, input_dims=[5], lr=0.003)
    scores = []
    eps_history = []
    num_games = 500
    score = 0

    for i in range(num_games):
        score = 0
        done = False

        # Initial observation/states/vehs is a random draft from initial conditions
        observation = [[196.1, 0., 8., 5.08, 1., 0],
             [187.92,  0.,   8.,    4.28,  2., 0],
             [179.94,  0.,    8.,    5.22,  1.8, 0],
             [169.92,  0.,    8.,    4.54,  2., 0],
             [161.48,  0.,    8.,    4.63,  2., 0],
             [153.45,  0.,    8.,    5.85,  1.5, 0],
             [144.3,   0.,    8.,    5.15,  1.8, 0],
             [135.65,  0.,    8.,    4.85,  1.8, 0],
             [126.9,   0.,    8.,    5.84, 1.5, 0],
             [116.96,  0.,    8.,    5.13,  1.8, 0],
             [108.53,  0.,    8.,    4.05,  2., 0],
             [4.9,   1.,    8.,    4.8,   1.8, 0],
             [13.5,   1.,    8.,    4.82,  1.8, 0],
             [21.52,  1.,   8.,    4.02,  2., 0],
             [29.74, 1.,    8.,   4.73,  2., 0],
             [39.07,  1.,    8.,    4.92,  1.8, 0],
             [47.49,  1.,    8.,    4.32,  2., 0],
             [56.71,  1.,    8.,    4.98,  1.8, 0],
             [65.9,  1.,    8.,    4.97,  1.8, 0],
             [74.26,  1.,    8.,    4.58,  2., 0],
             [81.94,  1.,    8.,    4.05,  2., 0],
             [90.19,  1.,   8.,    4.92,  1.8, 0]]

        while not done:
            # Select action based on chooseAction
            action = agent.choose_action(observation)
            # Step function, recording how states transform
            observation_, reward, done = step(observation, action)

            score += reward
            agent.store_transition(observation, action, reward, observation_, done)
            observation = observation_
            agent.learn()

        scores.append(score)

        eps_history.append(agent.epsilon)
        avg_score = np.mean(scores[-100:])

    print('episode ', i, 'score %.2f' % score,
          'average score %.2f' % avg_score,
          'epsilon %.2f' % agent.epsilon)
    """ Plot the learning curve
    """
    x = [i+1 for i in range(num_games)]
    filename = 'vehicle_coordination.png'
    plotLearning(x, scores, eps_history, filename)
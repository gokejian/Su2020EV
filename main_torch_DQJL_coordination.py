# -*- coding: utf-8 -*-
"""Author: Haoran Su
Email: hs1854@nyu.edu
"""
import gym
from DQN_Agent import DeepQNetwork, Agent
from utils import plotLearning
import numpy as np
from gym import wrappers

L = 200
l_gap = 2
delta_t = 0.5

"""
Vehicle: state of the vehicle
"""
def calculate_reward(vehs):
    """
    Calculate reward for the given state
    :param vehs:
    :return: reward, a scalar for this timestamp
    """
    num_vehs = len(vehs)
    reward = 0
    # First, we want to check collision:
    for i in range(num_vehs):
        for j in range(i+1, num_vehs):
            # Front pos of veh i:
            front_pos = vehs[i][0]
            # Back pos of veh j:
            back_pos = vehs[j][0] - vehs[j][3]
            if front_pos + l_gap > back_pos and vehs[i][1] == vehs[j][i]:
                reward = -1000
    # If any vehicle is on lane 0 and vehicle position has not exceed the roadway length:
    for veh in vehs:
        if veh[1] == 0 and (veh[0] + veh[3] <= L):
            reward = -1

    return reward


def random_deceleration(most_comfortable_deceleration, lane_pos):
    """
    Return a deceleration based on given attribute of the vehicle
    :param most_comfortable_deceleration: the given attribute of the vehicle
    :param lane_pos: y
    :return: a deceleration adopted by human driver
    """
    if lane_pos:
        sigma = 0.2
    else:
        sigma = 0.4
    return np.random.normal(most_comfortable_deceleration, sigma)


def step(vehs, action):
    """
    State Transition function to compute the next state
    :param vehs: old state, i.e. vehs
    :param action: action associated
    :return: observation_,(next_state) reward, done(whether the process has completed)
    """
    observation_ = []
    num_vehs = len(vehs)

    for i in range(num_vehs):
        action_i = action[i]
        new_x = vehs[i][0] + vehs[i][2] * delta_t
        # Generate the actual deceleration adopted by human driver:
        b_actual = random_deceleration(vehs[i][4], vehs[i][1])
        # Velocity cannot be negative
        new_v = max(0, vehs[i][2] + b_actual * delta_t)
        # New position for vehicles who pulled over
        new_y = (vehs[i][1] == 0) and (new_v == 0) and (action_i == 1)

        new_veh = [new_x, new_y, new_v, vehs[i][3], vehs[i][4]]
        observation_.append(new_veh)

    reward = calculate_reward(observation_)

    # Check if the process has completed by examine no vehicles are on lane 0:
    flag = False
    for veh in observation_:
        if veh[2] == 0:
            flag = True

    done = (flag == False)
    return observation_, reward, done


# Main:
if __name__ == '__main__':
    env = gym.make('LunarLander-v2')
    brain = Agent(gamma=0.99, epsilon=1.0, batch_size=64, n_actions=4,
                  input_dims=[8], alpha=0.003)

    scores = []
    eps_history = []
    num_games = 500
    score = 0

    for i in range(num_games):
        if i % 10 == 0 and i > 0:
            avg_score = np.mean(scores[max(0, i-10):(i+1)])
            print('episode: ', i,'score: ', score,
                 ' average score %.3f' % avg_score,
                'epsilon %.3f' % brain.EPSILON)
        else:
            print('episode: ', i,'score: ', score)
        eps_history.append(brain.EPSILON)
        done = False

        # Initial observation/states/vehs is a random draft from initial conditions
        observation = env.reset()
        score = 0
        while not done:
            action = brain.chooseAction(observation)
            observation_, reward, done = step(observation, action)
            score += reward
            brain.storeTransition(observation, action, reward, observation_,
                                  done)
            observation = observation_
            brain.learn()

        scores.append(score)

    x = [i+1 for i in range(num_games)]
    filename = str(num_games) + 'Games' + 'Gamma' + str(brain.GAMMA) + \
               'Alpha' + str(brain.ALPHA) + 'Memory' + \
                str(brain.Q_eval.fc1_dims) + '-' + str(brain.Q_eval.fc2_dims) +'.png'
    plotLearning(x, scores, eps_history, filename)
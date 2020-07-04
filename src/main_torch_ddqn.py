# -*- coding: utf-8 -*-
"""Author: Haoran Su
Email: hs1854@nyu.edu
"""
# Ignore warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
from DDQN_Agent import Agent
from utils import plotLearning
import RoadEnv

if __name__ == '__main__':

    env = RoadEnv()

    # Set the number of games
    num_games = 100

    # If load trained parameters from pre-trained models
    load_checkpoint = False

    # Initialize DDQN agent
    agent = Agent(gamma=0.99, epsilon=1.0, lr=5e-4,
                  input_dims=[15, 6], n_actions=2**15, mem_size=100000, eps_min=0.01,
                  batch_size=32, eps_dec=1e-3, replace=100)

    if load_checkpoint:
        agent.load_models()

    filename = 'DQJL-Duelling-Adam-lr0005-replace100e.png'
    scores = []
    eps_history = []
    n_steps = 0

    for i in range(num_games):
        done = False

        # reset state
        observation = env.reset()

        score = 0

        while not done:
            action = agent.choose_action(observation)
            observation_, reward, done = env.step(observation, action)
            n_steps += 1
            score += reward
            agent.store_transition(observation, action, reward, observation_, done)
            agent.learn()
            # update state
            observation = observation_

        scores.append(score)
        avg_score = np.mean(scores[max(0, i-100):(i+1)])
        print('episode: ', i,'score %.1f ' % score, ' average score %.1f' % avg_score, 'epsilon %.2f' % agent.epsilon)
        if i > 0 and i % 10 == 0:
            agent.save_models()
        eps_history.append(agent.epsilon)

    x = [i+1 for i in range(num_games)]
    plotLearning(x, scores, eps_history, filename)
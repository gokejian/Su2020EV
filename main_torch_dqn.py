# -*- coding: utf-8 -*-
"""Author: Haoran Su
Email: hs1854@nyu.edu
"""
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
from DQN_Agent import Agent
from utils import plotLearning
import Processing

observation = [[196.1, 0., 8., 5.08, 1., 0],
               [187.92, 0., 8., 4.28, 2., 0],
               [179.94, 0., 8., 5.22, 1.8, 0],
               [108.53, 0., 8., 4.05, 2., 0]]

# Map the given state into size of 10
observation = Processing.mapped_state(observation)


if __name__ == '__main__':

    num_games = 100
    load_checkpoint = False

    agent = Agent(gamma=0.99, epsilon=1.0, lr=5e-4,
                  input_dims=[5, 6], n_actions=2**5, max_mem_size=100000, eps_end=0.05,
                  batch_size=32, eps_dec=1e-3)

    if load_checkpoint:
        agent.load_models()

    filename = 'DQJL-Adam-lr0005-replace100e.png'
    scores = []
    eps_history = []
    n_steps = 0

    for i in range(num_games):
        done = False
        # observation = env.reset()
        score = 0

        while not done:
            action = agent.choose_action(observation)
            observation_, reward, done = Processing.step(observation, action)
            n_steps += 1
            score += reward
            agent.store_transition(observation, action, reward, observation_, int(done))
            agent.learn()

            observation = observation_
        scores.append(score)
        avg_score = np.mean(scores[max(0, i-100):(i+1)])
        print('episode: ', i,'score %.1f ' % score,
             ' average score %.1f' % avg_score,
            'epsilon %.2f' % agent.epsilon)
        # if i > 0 and i % 10 == 0:
        #    agent.save_models()
        eps_history.append(agent.epsilon)

    x = [i+1 for i in range(num_games)]
    plotLearning(x, scores, eps_history, filename)
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
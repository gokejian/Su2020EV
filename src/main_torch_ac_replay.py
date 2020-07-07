# -*- coding: utf-8 -*-
"""Author: Haoran Su
Email: hs1854@nyu.edu
"""
import gym
import numpy as np
from actor_critic_replay_torch import Agent
from utils_ac import plotLearning
from RoadEnv import RoadEnv

if __name__ == '__main__':
    env = RoadEnv()
    num_games = 1500
    agent = Agent(gamma=0.99, lr=1e-5, input_dims=[10, 6], n_actions=2**10,
                  l1_size=256, l2_size=256)

    filename = 'LunarLander-ActorCriticNaiveReplay-256-256-Adam-lr00001.png'
    scores = []

    for i in range(num_games):
        done = False
        observation = env.reset()
        score = 0

        while not done:
            action, prob = agent.choose_action(observation)
            observation_, reward, done = env.step(observation, action)
            score += reward
            agent.store_transition(observation, prob, reward, observation_, int(done))
            agent.learn()
            observation = observation_

        scores.append(score)
        avg_score = np.mean(scores[max(0, i-100):(i+1)])
        print('episode: ', i,'score %.1f ' % score,
             ' average score %.1f' % avg_score)

    x = [i+1 for i in range(num_games)]
    plotLearning(scores, filename, x)
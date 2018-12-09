#!/usr/bin/env python3

"""
Simple example of using cherry to solve cartpole with an actor-critic.

The code is an adaptation of the PyTorch reinforcement learning example.
"""

import random
import gym
import numpy as np

from itertools import count

import torch as th
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical

import cherry as ch
import cherry.envs as envs
from cherry.rewards import discount_rewards
from cherry.utils import normalize

SEED = 567
GAMMA = 0.99
RENDER = False
V_WEIGHT = 0.5

random.seed(SEED)
np.random.seed(SEED)
th.manual_seed(SEED)


class ActorCriticNet(nn.Module):
    def __init__(self):
        super(ActorCriticNet, self).__init__()
        self.affine1 = nn.Linear(4, 128)
        self.action_head = nn.Linear(128, 2)
        self.value_head = nn.Linear(128, 1)

    def forward(self, x):
        x = F.relu(self.affine1(x))
        action_scores = self.action_head(x)
        action_mass = Categorical(F.softmax(action_scores, dim=1))
        value = self.value_head(x)
        return action_mass, value


def finish_episode(replay, optimizer):
    policy_loss = []
    value_loss = []

    # Discount and normalize rewards
    rewards = discount_rewards(GAMMA, replay.list_rewards, replay.list_dones)
    rewards = normalize(th.tensor(rewards))

    # Compute losses
    for info, reward in zip(replay.list_infos, rewards):
        log_prob = info['log_prob']
        value = info['value']
        policy_loss.append(-log_prob * (reward - value.item()))
        value_loss.append(F.mse_loss(value, reward.detach()))

    # Take optimization step
    optimizer.zero_grad()
    loss = th.stack(policy_loss).sum() + V_WEIGHT * th.stack(value_loss).sum()
    loss.backward()
    optimizer.step()


if __name__ == '__main__':
    env = gym.make('CartPole-v0')
    env = envs.Logger(env, interval=1000)
    env = envs.Normalized(env)
    env = envs.Torch(env)
    env.seed(SEED)

    policy = ActorCriticNet()
    optimizer = optim.Adam(policy.parameters(), lr=1e-2)
    running_reward = 10.0
    replay = ch.ExperienceReplay()

    for i_episode in count(1):
        state = env.reset()
        for t in range(10000):  # Don't infinite loop while learning
            mass, value = policy(state)
            action = mass.sample()
            old_state = state
            state, reward, done, _ = env.step(action)
            replay.add(old_state, action, reward, state, done, info={
                'log_prob': mass.log_prob(action),  # Cache log_prob for later
                'value': value
            })
            if RENDER:
                env.render()
            if done:
                break

        # Compute termination criterion
        running_reward = running_reward * 0.99 + t * 0.01
        if running_reward > env.spec.reward_threshold:
            print('Solved! Running reward is now {} and '
                  'the last episode runs to {} time steps!'.format(running_reward, t))
            break

        # Update policy
        finish_episode(replay, optimizer)
        replay.empty()
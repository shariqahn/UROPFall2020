import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from random import randint, choice

class FooEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    
    self.map = [['','','','.'],['.','.','.','.'],['','','.','.'],['.','','','G']]
    self.state = [0,0]
    self.reward = 0
    self.done = False
    self.action_space = ['right', 'left', 'up', 'down'] #use openai action spaces instead!!!
    self.pellet_reward = -2
    self.space_reward = -1

    rewards = {}
    for i in range(len(self.map)):
      for j in range(len(self.map[0])):
        if self.map[i][j] == '.':
          rewards[str([i,j])] = self.pellet_reward
        elif self.map[i][j] == '':
          rewards[str([i,j])] = self.space_reward
        else:
          rewards[str([i,j])] = 10


    self.reward_function = rewards

  def randomize_rewards(self): 
    # make all rewards negative except the goal
    # make pellets half the map, rather than 3
    # make all pellets less/more negative than empty spaces, but all should be negative
      # will be useful when querying
    pellet_reward = choice([-50,-1])
    while True:
      reward = choice([-50,-1])
      if reward != pellet_reward:
        space_reward = reward
        break

    self.pellet_reward = pellet_reward
    self.space_reward = space_reward

    rewards = {}
    for i in range(len(self.map)):
      for j in range(len(self.map[0])):
        if self.map[i][j] == '.':
          rewards[str([i,j])] = pellet_reward
        elif self.map[i][j] == '':
          rewards[str([i,j])] = space_reward
        else:
          rewards[str([i,j])] = 10

    self.reward_function = rewards
    return rewards

  def randomize_map(self):
    new_map = [['','','',''],['','','',''],['','','',''],['','','','']]
    for i in range(8):
      row = randint(0,3)
      column = randint(0,3)
      while new_map[row][column] == '.':
        row = randint(0,3)
        column = randint(0,3)
      new_map[row][column] = '.'

    goal_row = randint(0,3)
    goal_column = randint(0,3)
    while new_map[goal_row][goal_column] == '.':
      goal_row = randint(0,3)
      goal_column = randint(0,3)
    new_map[goal_row][goal_column] = 'G'  

    self.map = new_map
    return new_map

  def step(self, action):
    if action == 'right':
      self.state[1] = (self.state[1] + 1) % 4
    elif action == 'left':
      self.state[1] = (self.state[1] + 3) % 4
    elif action == 'up':
      self.state[0] = (self.state[0] + 3) % 4
    else:
      self.state[0] = (self.state[0] + 1) % 4

    reward = self.reward_function[str([self.state[0], self.state[1]])]
    self.reward += reward
    # self.map[self.state[0]][self.state[1]] = ""
    if self.map[self.state[0]][self.state[1]] == "G":
      self.done = True

    return str(self.state), reward, self.done, self.map

  def reset(self):
    # self.map = [['','','',''],['.','.','.','G'],['','','',''],['','','','']]
    self.state = [0,0] 
    self.reward = 0
    self.done = False
    return str(self.state)

  def render(self, mode='human', close=False):
    print(self.state, self.reward)
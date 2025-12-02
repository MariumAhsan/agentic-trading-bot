import gym
import numpy as np
import pandas as pd
from gym import spaces


class TradingEnv(gym.Env):
    def __init__(self, df):
        super(TradingEnv, self).__init__()

        self.df = df.reset_index(drop=True)
        self.current_step = 0

        # Price only (you can add indicators later)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32
        )

        # Actions: 0 = hold, 1 = buy, 2 = sell
        self.action_space = spaces.Discrete(3)

        self.balance = 10000
        self.shares = 0

    def _get_obs(self):
        return np.array([self.df["close"][self.current_step]])

    def step(self, action):
        price = self.df["close"][self.current_step]

        reward = 0

        if action == 1:  # Buy
            self.shares += 1
            self.balance -= price

        elif action == 2 and self.shares > 0:  # Sell
            self.shares -= 1
            self.balance += price
            reward = price  # Profit = reward

        self.current_step += 1
        done = self.current_step >= len(self.df) - 1

        return self._get_obs(), reward, done, {}

    def reset(self):
        self.current_step = 0
        self.balance = 10000
        self.shares = 0
        return self._get_obs()

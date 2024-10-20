import gymnasium as gym
from gymnasium import spaces
import numpy as np

class NotificationTimingEnv(gym.Env):
    def __init__(self):
        super(NotificationTimingEnv, self).__init__()
        
        # State: Time of the day (continuous between 0 and 1)
        self.observation_space = spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
        
        # Action: Discrete action space (0 or 1)
        self.action_space = spaces.Discrete(2)
        
        # Initialize time of day
        self.time_of_day = np.random.uniform(0, 1)

    def reset(self, seed=None):
        self.time_of_day = np.random.uniform(0, 1)
        
        # Return the initial observation
        return np.array([self.time_of_day], dtype=np.float32), {}
    
    def step(self, action):
        # The action is either 0 or 1
        send_notification = action
        
        # Reward: 1 if action is 1 and time is between 0.5-0.6, -1 otherwise
        if send_notification == 1 and 0.5 <= self.time_of_day:
            reward = 1
        elif send_notification == 0 and self.time_of_day < 0.5:
            reward = 1
        else:
            reward = -1
        
        # Update the time of day (e.g., advance by a small amount)
        self.time_of_day = self.time_of_day + 0.1
        
        # The episode ends after each step
        if self.time_of_day > 1: done = True
        else: done = False

        # Return the next state, reward, and done flag
        return np.array([self.time_of_day], dtype=np.float32), reward, done, False, {}
    
    def render(self, mode="human"):
        print(f"Time of day: {self.time_of_day}")
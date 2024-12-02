import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import pandas as pd

# Example dataset (replace this with actual data loading)
data = pd.read_csv("../collected_dataset/cleaned_dataset.csv")

class NotificationTimingEnv(gym.Env):
    def __init__(self):
        super(NotificationTimingEnv, self).__init__()

        # State: Time of the day (continuous between 0 and 1)
        self.observation_space = spaces.Dict(
            {
                "time_of_day": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
                "app_type": spaces.Discrete(2),  # 0: app X, 1: app Y
            }
        )
        # Action: Discrete action space (0 or 1) where 0 means no notification, 1 means send notification
        self.action_space = spaces.Discrete(2)

        # Initialize time of day
        self.time_of_day = 0
        self.app_type = 0

        # Your dataset index
        self.data_index = 0

    def reset(self, seed=None):
        self.time_of_day = 0
        self.app_type = random.choice([0, 1])  # Randomly pick app type (0 or 1)
        self.data_index = 0  # Reset dataset index
        
        return {
            "time_of_day": np.array([self.time_of_day], dtype=np.float32),
            "app_type": self.app_type,
        }, {}

    def step(self, action):
        # The action is either 0 or 1 (whether to send a notification)
        send_notification = action
        
        # Get current data from the dataset (this will be used to simulate user behavior)
        arrival_time = data.loc[self.data_index, 'arrival_time_normalized']
        click_time = data.loc[self.data_index, 'interaction_time_normalized']
        self.app_type = data.loc[self.data_index, 'app_name_numeric']
        
        # Reward logic: Only send a reward if the time_of_day matches the click_time
        if send_notification == 1 and abs(self.time_of_day - click_time) < 0.01:
            reward = 1  # Positive reward if the time matches the click time
        else:
            reward = -1  # Negative reward for not matching or not sending a notification
            # Do not increment dataset index if no successful notification
            self.data_index = self.data_index  # Keeps the current row
        # Increment dataset index only after a successful notification send
        self.data_index = (self.data_index + 1) % len(data)

        # Simulate the next state of the environment (e.g., time of day progresses)
        next_state, is_day_done = self.simulate_state_of_env()

        return next_state, reward, is_day_done, False, {}

    def render(self, mode="human"):
        print(f"Time of day: {self.time_of_day}, App type: {self.app_type}")

    def simulate_state_of_env(self):
        # Simulate the time of day progressing (increasing slightly each step)
        self.time_of_day = self.time_of_day + 0.000695
        
        # The episode ends when time_of_day exceeds 1 (end of day)
        if self.time_of_day > 1:
            done = True
        else:
            done = False
        
        return {
            "time_of_day": np.array([self.time_of_day], dtype=np.float32),
            "app_type": self.app_type,
        }, done

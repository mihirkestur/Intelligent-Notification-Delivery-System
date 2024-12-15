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
        self.location_to_int = {
            "HOME": 0,
            "LIBRARY": 1,
            "UNIVERSITY": 2,
            "UNKNOWN": 3,
        }

        # State: Time of the day (continuous between 0 and 1)
        self.observation_space = spaces.Dict(
            {
                "time_of_day": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
                "app_type": spaces.Discrete(2),  # 0: app X, 1: app Y,
                "location": spaces.Discrete(
                    4
                ),  # 0: HOME, 1: LIBRARY, 2: UNIVERSITY, 3: UNKNOWN
            }
        )
        # Action: Discrete action space (0 or 1) where 0 means no notification, 1 means send notification
        self.action_space = spaces.Discrete(2)

        # Initialize time of day
        self.time_of_day = 0
        self.app_type = 0
        self.location = 0

    def reset(self, seed=None):
        self.time_of_day = 0
        self.location = 0
        self.app_type = random.choice([0, 1])  # Randomly pick app type (0 or 1)
        self.data_index = 0  # Reset dataset index

        return {
            "time_of_day": np.array([self.time_of_day], dtype=np.float32),
            "app_type": self.app_type,
            "location": self.location,
        }, {}

    def step(self, action):
        # The action is either 0 or 1 (whether to send a notification)
        send_notification = action

        # Simulate the next state of the environment (e.g., time of day progresses)
        next_state, is_day_done = self.simulate_state_of_env()

        # Get current data from the dataset (this will be used to simulate user behavior)
        # arrival_time = data.loc[self.data_index, 'arrival_time_normalized']
        # click_time = data.loc[self.data_index, 'interaction_time_normalized']
        # self.app_type = data.loc[self.data_index, 'app_name_numeric']
        user_action = self.simulate_user(
            next_state["app_type"],
            next_state["time_of_day"],
            next_state["location"],
        )
        # Reward logic: Only send a reward if the time_of_day matches the click_time
        if send_notification == 1 and user_action == 1:
            reward = 1  # Positive reward if the time matches the click time
            # Increment dataset index only after a successful notification send
            # self.data_index = (self.data_index + 1) % len(data)
        elif send_notification == 0 and user_action == 0:
            reward = -0.001
        elif send_notification == 1 and user_action == 0:
            reward = -0.01
        else:
            reward = -1

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
            "app_type": random.randint(0, 1),
            "location": random.randint(0, 3),
        }, done

    def location_str_to_int(self, loc: str) -> int:
        return self.location_to_int[loc]

    def simulate_user(self, app_name, timestamp, location):
        clicked_time_window = 15 / (
            24 * 60
        )  # 5 minutes in normalized time (1 day = 1.0)
        app_records = data[data["app_name_cleaned"] == app_name]
        timestamp_normalized = timestamp

        for _, row in app_records.iterrows():
            if row["reason_mapped"] == "clicked" and row[
                "location_name"
            ] == self.location_str_to_int(location):
                time_difference = abs(
                    row["interaction_time_normalized"] - timestamp_normalized
                )
                if time_difference <= clicked_time_window:
                    return True
        return False

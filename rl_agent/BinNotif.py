import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class NotificationTimingEnv(gym.Env):
    def __init__(self):
        super(NotificationTimingEnv, self).__init__()

        # State: Time of the day (continuous between 0 and 1)
        self.observation_space = spaces.Dict(
            {
                "time_of_day": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
                "location": spaces.Discrete(4),
                "activity": spaces.Discrete(3),
                "app_type": spaces.Discrete(2),  # 0: app X, 1: app Y
            }
        )
        # spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)

        # Action: Discrete action space (0 or 1)
        self.action_space = spaces.Discrete(2)

        # Initialize time of day
        self.time_of_day = 0

        self.location = 2 # np.random.choice([0, 1, 2, 3])  # home, school, library, unknown

        self.activity = 2 # np.random.choice([0, 1, 2])  # running, walking, still

        # App type
        self.app_type = 0

    def reset(self, seed=None):
        self.time_of_day = 0

        self.location = 2 # np.random.choice([0, 1, 2, 3])  # home, school, library, unknown

        self.activity = 2 # np.random.choice([0, 1, 2])  # running, walking, still
        self.app_type = 0
        # Return the initial observation
        return {
            "time_of_day": np.array([self.time_of_day], dtype=np.float32),
            "location": self.location,
            "activity": self.activity,
            "app_type": self.app_type,
        }, {}

    def step(self, action):
        # The action is either 0 or 1
        send_notification = action

        if (
            send_notification == 1 and self.simulate_user() == 1
        ):  
            reward = 1
        elif send_notification == 0 and self.simulate_user() == 0:
            reward = -0.001
        else:
            reward = -1

        next_state, is_day_done = self.simulate_state_of_env()

        # Return the next state, reward, and done flag
        return next_state, reward, is_day_done, False, {}

    def render(self, mode="human"):
        print(f"Time of day: {self.time_of_day}")

    def simulate_user(self):
        uni_arrival_time = 0.46
        library_arrival_time = 0.76
        home_return_time = 0.8333
        if self.time_of_day < 0.29167:  # Before 7 AM
            return 0
        elif self.time_of_day < 0.45833:  # 7 AM - 11 AM
            if (
                self.location == self.location_encoding("home")
                and self.activity == self.activity_encoding("still")
                and self.app_type == 0
            ):
                return 1
            else:
                return 0
        elif self.time_of_day < 0.75:  # 11 AM - 6 PM
            if self.location == self.location_encoding(
                "unknown"
            ) and self.activity == self.activity_encoding("walking"):
                return 1
            else:
                return 0
        elif self.time_of_day < home_return_time:  # 6 PM - 8 PM
            if (
                self.location == self.location_encoding("library")
                and self.activity == self.activity_encoding("still")
                and self.app_type == 1
            ):
                return 1
            else:
                return 0
        elif self.time_of_day < 0.95833:  # 8 PM - 11 PM
            if self.location == self.location_encoding("home"):
                return 1
            else:
                return 0
        else:  # After 11 PM
            return 0

    def activity_encoding(self, walking_str) -> int:
        if walking_str == "still":
            return 2
        elif walking_str == "walking":
            return 1
        else:
            return 0

    def location_encoding(self, location_str) -> int:
        if location_str == "unknown":
            return 0
        elif location_str == "university":
            return 1
        elif location_str == "home":
            return 2
        else:
            return 3

    def simulate_state_of_env(self):
        # Simulate what the user does
        self.time_of_day = self.time_of_day + 0.000695
        uni_arrival_time = 0.46
        library_arrival_time = 0.76
        home_return_time = 0.8333
        returned_home = False

        # The episode ends after each step
        if self.time_of_day > 1:
            done = True
        else:
            done = False

        if self.time_of_day < 0.29167:  # Before 7 AM
            self.activity = self.activity_encoding("still")
            self.location = self.location_encoding("home")
            
        elif self.time_of_day < 0.45833:  # 7 AM - 11 AM
            self.activity = self.activity_encoding("still")
            self.location = self.location_encoding("home")

        elif self.time_of_day < 0.75:  # 11 AM - 6 PM
            if self.time_of_day < uni_arrival_time:
                self.activity = self.activity_encoding(
                    random.choice(["walking", "running"])
                )
                self.location = self.location_encoding("unknown")
            else:
                self.location = self.location_encoding("university")
                if random.random() < 0.3:  # 30% chance to walk randomly
                    self.activity = self.activity_encoding("walking")
                else:
                    self.activity = self.activity_encoding("still")
            
        elif self.time_of_day < home_return_time:  # 6 PM - 8 PM
            if self.time_of_day < library_arrival_time:
                self.activity = self.activity_encoding(
                    random.choice(["walking", "running"])
                )
                self.location = self.location_encoding("unknown")

            else:
                self.location = self.location_encoding("library")
                if random.random() < 0.1:  # 10% chance to walk randomly in library
                    self.activity = self.activity_encoding("walking")
                else:
                    self.activity = self.activity_encoding("still")
            
        elif self.time_of_day < 0.95833:  # 8 PM - 11 PM
            if not returned_home:
                if (
                    self.time_of_day < home_return_time + 0.0208
                ):  # 30 minutes to return home
                    self.activity = self.activity_encoding(random.choice(["walking", "running"]))
                    self.location = self.location_encoding("unknown")
                else:
                    returned_home = True
                    self.activity = self.activity_encoding("still")
                    self.location = self.location_encoding("home")
            else:
                self.activity = self.activity_encoding("still")
                self.location = self.location_encoding("home")
            
        else:  # After 11 PM
            self.activity = self.activity_encoding("still")
            self.location = self.location_encoding("home")
            
        self.app_type = random.randint(0, 1)
        
        return {
            "time_of_day": np.array([self.time_of_day], dtype=np.float32),
            "location": self.location,
            "activity": self.activity,
            "app_type": self.app_type,
        }, done

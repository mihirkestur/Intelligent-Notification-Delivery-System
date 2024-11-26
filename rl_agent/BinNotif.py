import gymnasium as gym
from gymnasium import spaces
import numpy as np

class NotificationTimingEnv(gym.Env):
    def __init__(self):
        super(NotificationTimingEnv, self).__init__()
        
        # State: Time of the day (continuous between 0 and 1)
        self.observation_space = spaces.Dict({
            'time_of_day': spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
            'app_type': spaces.Discrete(2)  # 0: app X, 1: app Y
        })
        # spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
        
        # Action: Discrete action space (0 or 1)
        self.action_space = spaces.Discrete(2)
        
        # Initialize time of day
        self.time_of_day = np.random.uniform(0, 1)

        self.location = np.random.choice([0, 1, 2, 3]) # home, school, library, unknown

        self.activity = np.random.choice([0, 1, 2]) # running, walking, still

        # App type
        self.app_type = np.random.choice([0, 1])

    def reset(self, seed=None):
        self.time_of_day = np.random.uniform(0, 1)
        self.app_type = np.random.choice([0, 1])
        # Return the initial observation
        return {
            'time_of_day': np.array([self.time_of_day], dtype=np.float32),
            'app_type': self.app_type
        }, {}
    
    def step(self, action):
        # The action is either 0 or 1
        send_notification = action
        
        # Reward: 1 if action is 1 and time is between 0.5-0.6, -1 otherwise
        if send_notification == 1 and self.simulate_user() == 1: # 0.5 <= self.time_of_day:
            reward = 1
        elif send_notification == 0 and self.simulate_user() == 0:
            reward = -0.01
        else:
            reward = -1

        next_state, is_day_done = self.simulate_state_of_env()

        # Return the next state, reward, and done flag
        return next_state, reward, is_day_done, False, {}
    
    def render(self, mode="human"):
        print(f"Time of day: {self.time_of_day}")
    
    def simulate_user(self):
        if self.app_type == 0:
            if 0.5 <= self.time_of_day <= 0.7:
                return 1
            else:
                return 0
        else:
            if 0.3 <= self.time_of_day <= 0.5:
                return 1
            else:
                return 0
    
    def simulate_state_of_env(self):
        # Simulate what the user does 
        
        # Update the time of day (e.g., advance by a small amount)
        self.time_of_day = self.time_of_day + 0.000695
        # The episode ends after each step
        if self.time_of_day > 1: done = True
        else: done = False
        
        # self.location = np.random.choice([0, 1, 2, 3]) # home, school, library, unknown

        # self.activity = np.random.choice([0, 1, 2]) # running, walking, still

        # i sleep 

        return {
            'time_of_day': np.array([self.time_of_day], dtype=np.float32),
            'location': self.location,
            'activity': self.activity,
            'app_type': self.app_type
        }, done
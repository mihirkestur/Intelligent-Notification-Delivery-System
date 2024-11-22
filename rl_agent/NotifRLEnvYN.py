import numpy as np
from gymnasium import spaces, Env

class NotificationTimingEnv(Env):
    def __init__(self):
        super(NotificationTimingEnv, self).__init__()
        
        self.observation_space = spaces.Dict({
            'time_of_day': spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
            'app_type': spaces.Discrete(2)  # 0: app X, 1: app Y
        })
        self.action_space = spaces.Discrete(2)  # 0: do not send, 1: send now
        self.app_type = None
        self.current_hour = None
        self.episode_length = 1
        self.send_notification = False

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.app_type = np.random.randint(0, 2)
        self.current_hour = 0
        self.send_notification = False
        return self._get_obs(), self._get_info()

    def step(self, action):
        if action == 1:  # If action is to send
            if self.simulate_user_behaviour(self.current_hour, self.app_type):
                reward = 1
            else:
                reward = -1
        else:
            if self.simulate_user_behaviour(self.current_hour, self.app_type):
                reward = -1
            else:
                reward = 0.5
        
        # # Move to the next hour
        # self.current_hour += (1/24)
        # done = self.current_hour >= self.episode_length

        return self._get_obs(), reward, True, False, self._get_info()

    def _get_obs(self):
        return {
            'time_of_day': np.array([self.current_hour], dtype=np.float32),
            'app_type': self.app_type
        }

    def _get_info(self):
        return {}

    def render(self, mode="human"):
        print(f"Current Hour: {self.current_hour}, App Type: {self.app_type}, Notification Sent: {self.send_notification}")

    def simulate_user_behaviour(self, time_of_day, app_type):
        if app_type == 0:  # App X
            return 0.1 <= time_of_day <= 0.4
        else:  # App Y
            return 0.6 <= time_of_day <= 1
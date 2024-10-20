import gymnasium as gym
from gymnasium import spaces
import numpy as np

class NotificationTimingEnv(gym.Env):
    def __init__(self):
        super(NotificationTimingEnv, self).__init__()
        
        # State: Time of the day when the agent can send a notification (continuous between 0 and 1)
        # self.observation_space = spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
        self.observation_space = spaces.Dict({
            'time_of_day': spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
            'app_type': spaces.Discrete(2)  # 0: app X, 1: app Y
        })
        
        # Action: Time to send a notification (continuous between 0 and 1)
        self.action_space = spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
        
        # Initialize Send Notification Time 
        self.send_notification_time = np.random.uniform(0, 1)
        self.app_type = np.random.choice([0, 1])

    def reset(self, seed=None):
        self.send_notification_time = np.random.uniform(0, 1)
        self.app_type = np.random.choice([0, 1])  # Randomly set the app (app X or app Y)
        
        # Return the initial observation
        return {
            'time_of_day': np.array([self.send_notification_time], dtype=np.float32),
            'app_type': self.app_type
        }, {}
    
    def step(self, action):
        # The action represents the time to send the notification (between 0 and 1)
        notification_send_prediction = action[0]
        
        # Simulate the actual open time based on the arrival time
        actual_open_time = self.simulate_open_time(notification_send_prediction)
        
        time_diff = abs(notification_send_prediction - actual_open_time)
        # Reward: Negative absolute difference between actual open time and notification time
        if notification_send_prediction in [(actual_open_time-0.001), (actual_open_time+0.001)]: reward = 1 
        else: reward = -time_diff # -np.exp(time_diff / 60) # abs(notification_send_prediction - actual_open_time)
        
        # Update the Send Notification Time to simulate the passage of time (e.g., advance by 1 hour)
        self.send_notification_time = notification_send_prediction
        
        # The episode ends 
        done = 1

        # Return the next state (Send Notification Time), reward, and done flag
        # return np.array([self.send_notification_time], dtype=np.float32), reward, done, False, {}
        return {
            'time_of_day': np.array([self.send_notification_time], dtype=np.float32),
            'app_type': self.app_type
        }, reward, done, False, {}
        
    
    def render(self, mode="human"):
        # Print Send Notification Time and action
        print(f"Send Notification Time: {self.send_notification_time}")

    # Example function to simulate the open time based on notification arrival time
    def simulate_open_time(self, notif_arrive_time):
        if self.app_type == 0:
            return 0.5
        else:
            return 0.9
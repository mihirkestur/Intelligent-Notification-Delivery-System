from stable_baselines3 import PPO, DDPG, DQN
# from NotifRLEnv import NotificationTimingEnv
# from NotifRLEnvYN import NotificationTimingEnv
from BinNotif import NotificationTimingEnv
import numpy as np
# Create the environment
env = NotificationTimingEnv()

from stable_baselines3.common.callbacks import BaseCallback
import numpy as np

from stable_baselines3.common.logger import configure

# Set up the path for logging
log_path = "./logs/"

# Configure the logger to use CSV format
new_logger = configure(log_path, ["csv"])

# # Train an RL agent
# model = DQN("MultiInputPolicy", env, verbose=1) # MultiInputPolicy
# # Set the new logger
# model.set_logger(new_logger)
# # model = PPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=1000000)
# # Save the model
# model.save("./models/plswork1")

# Load the saved model
# model = PPO.load("./models/notification_model")
model = DQN.load("./models/plswork1")
# # Test the trained agent
print("Time of Day", "\tApp Type", "Action")  
for i in range(1, 10):
    observation = {
        "time_of_day": np.array([i/10], dtype=np.float32),
        "app_type": np.array([1], dtype=np.float32),
        "location":2,
        "activity":2
    }
    print(observation)
    action, _states = model.predict(observation, deterministic=True)
    if action[0] == 0:
        print("Don't Send", end="\t")
    else:
        print("Send Now", end="\t")
    print("\n")
# print("Time of Day", "\tApp Type", "Action")
# for i in range(1, 10):
#     observation = {
#         "time_of_day": np.array([i/10], dtype=np.float32),
#         "app_type": np.array([1], dtype=np.float32),
#     }
#     print(observation["time_of_day"], observation["app_type"], sep='\t\t', end="\t")
#     action, _states = model.predict(observation, deterministic=True)
#     if action[0] == 0:
#         print("Don't Send", end="\t")
#     else:
#         print("Send Now", end="\t")
#     print("\n")
# # obs, _ = env.reset()
# # env.send_notification_time = np.array([99])
# # obs, reward, done, truncated, info = env.step(action)
# # print(obs, reward)
# # env.render()
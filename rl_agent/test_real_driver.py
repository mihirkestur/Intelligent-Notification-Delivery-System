from stable_baselines3 import PPO, DDPG, DQN
from test_real_dataset import NotificationTimingEnv
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
import numpy as np
from stable_baselines3.common.logger import configure
import csv
from user_response_speed import simulate_user

# Set up the path for logging
log_path = "./logs/"

# Configure the logger to use CSV format
new_logger = configure(log_path, ["csv"])

# Create the environment
env = NotificationTimingEnv()

# Train an RL agent
model = DQN("MultiInputPolicy", env, verbose=1) # MultiInputPolicy
# Set the new logger
model.set_logger(new_logger)
# model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=600000)
# Save the model
model.save("./models/test_real_dataset_1")

# # Load the trained model
# model = DQN.load("./models/test_real_dataset.zip")

# # Load the dataset
# dataset_filename = "../collected_dataset/cleaned_dataset.csv"

# acc = 0
  
# # Test the trained agent with dataset
# with open(dataset_filename, "r") as file:
#     reader = csv.DictReader(file)
#     for row in reader:
#         # Prepare observation from dataset row
#         observation = {
#             "time_of_day": np.array([float(row["interaction_time_normalized"])], dtype=np.float32),
#             "app_type": float(row["interaction_time_normalized"]),
#         }

#         # Predict action using the trained model
#         action, _states = model.predict(observation, deterministic=True)
    
#         if 1 == action: acc+=1

# print(100*acc/1440)

# # # Load the saved model
# # # model = PPO.load("./models/notification_model")
# # model = DQN.load("./models/plswork2")
# # # Test the trained agent
# # for i in [4]:#range(1, 10):
# #     observation = {
# #         "time_of_day": np.array([i/10], dtype=np.float32),
# #         "app_type": 1,
# #         "location":2,
# #         "activity":2
# #     }
# #     print(observation)
# #     action, _states = model.predict(observation, deterministic=True)
# #     if action == 0:
# #         print("Don't Send", end="\t")
# #     else:
# #         print("Send Now", end="\t")
# #     print("\n")
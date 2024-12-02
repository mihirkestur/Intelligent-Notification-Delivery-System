from stable_baselines3 import PPO, DDPG, DQN
from BinNotif import NotificationTimingEnv
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
import numpy as np
from stable_baselines3.common.logger import configure
import csv

# Set up the path for logging
log_path = "./logs/"

# Configure the logger to use CSV format
new_logger = configure(log_path, ["csv"])

# Create the environment
env = NotificationTimingEnv()

# Train an RL agent
# model = DQN("MultiInputPolicy", env, verbose=1) # MultiInputPolicy
# # Set the new logger
# model.set_logger(new_logger)
# # model = PPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=600000)
# # Save the model
# model.save("./models/plswork2")

# Load the trained model
model = DQN.load("./models/final")

# Load the dataset
dataset_filename = "./dataset_generation/user_behavior_dataset.csv"

def simulate_user(data):
    def activity_encoding(activity_str):
        if activity_str == "still":
            return 2
        elif activity_str == "walking":
            return 1
        else:
            return 0

    def location_encoding(location_str):
        if location_str == "unknown":
            return 0
        elif location_str == "university":
            return 1
        elif location_str == "home":
            return 2
        else:
            return 3

    time_of_day = data["time_of_day"]
    location = data["location"]
    activity = data["activity"]
    app_type = data["app_type"]

    home_return_time = 0.8333

    if time_of_day < 0.29167:  # Before 7 AM
        return 0
    elif time_of_day < 0.45833:  # 7 AM - 11 AM
        if (
            location == location_encoding("home")
            and activity == activity_encoding("still")
            and app_type == 0
        ):
            return 1
        else:
            return 0
    elif time_of_day < 0.75:  # 11 AM - 6 PM
        if location == location_encoding("unknown") and activity == activity_encoding("walking"):
            return 1
        else:
            return 0
    elif time_of_day < home_return_time:  # 6 PM - 8 PM
        if (
            location == location_encoding("library")
            and activity == activity_encoding("still")
            and app_type == 1
        ):
            return 1
        else:
            return 0
    elif time_of_day < 0.95833:  # 8 PM - 11 PM
        if location == location_encoding("home"):
            return 1
    else:  # After 11 PM
        return 0

acc = 0    
# Test the trained agent with dataset
with open(dataset_filename, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Prepare observation from dataset row
        observation = {
            "time_of_day": np.array([float(row["time_of_day"])], dtype=np.float32),
            "app_type": 1,
            "location": int(row["location"]),
            "activity": int(row["activity"])
        }

        # Predict action using the trained model
        action, _states = model.predict(observation, deterministic=True)
        open = simulate_user(observation)
        if open == action: acc+=1
print(100*acc/1440)

# # Load the saved model
# # model = PPO.load("./models/notification_model")
# model = DQN.load("./models/plswork2")
# # Test the trained agent
# for i in [4]:#range(1, 10):
#     observation = {
#         "time_of_day": np.array([i/10], dtype=np.float32),
#         "app_type": 1,
#         "location":2,
#         "activity":2
#     }
#     print(observation)
#     action, _states = model.predict(observation, deterministic=True)
#     if action == 0:
#         print("Don't Send", end="\t")
#     else:
#         print("Send Now", end="\t")
#     print("\n")
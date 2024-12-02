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
        else:
            return 0
    else:  # After 11 PM
        return 0


import csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Initialize variables
true_actions = []
predicted_actions = []

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
        # Store true and predicted actions
        predicted_actions.append(int(action))
        try:
            true_actions.append(int(open))
        except Exception:
            print(observation)

# Generate confusion matrix
cm = confusion_matrix(true_actions, predicted_actions)

# Create confusion matrix display
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Don't Send", "Send"])

# Plot confusion matrix
plt.figure(figsize=(8, 6))
disp.plot(cmap="Blues", values_format="d")
plt.title("Confusion Matrix: Predicted vs Actual Actions, App Type 1")
plt.savefig("confusion_matrix.png")
import streamlit as st
import numpy as np
from stable_baselines3 import DQN
import csv
from stable_baselines3.common.logger import configure
import datetime

# Load the trained model
model = DQN.load("./rl_agent/models/final")

# Load the dataset
dataset_filename = "./rl_agent/dataset_generation/user_behavior_dataset.csv"

# Streamlit App
st.title("Intelligent Notification Delivery System Demo")

# Input: Time in 24-hour format
time_input = st.text_input("Enter time in 24-hour format (HH:MM):", "14:30")

# Input: App Type (Email or WhatsApp)
app_type = st.selectbox("Select app type", ["Email", "WhatsApp"])

# Normalize the time function
def normalize_time(time_24hr):
    hours, minutes = map(int, time_24hr.split(":"))
    total_minutes = hours * 60 + minutes
    normalized_value = total_minutes / 1440
    return normalized_value

def denormalize_time(normalized_value):
    # Ensure normalized_value is a float
    normalized_value = float(normalized_value)

    # Calculate total minutes
    total_minutes = normalized_value * 1440
    
    # Convert total minutes to hours and minutes
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    
    # Format the time in HH:MM format
    denormalized_time = f"{hours:02}:{minutes:02}"
    
    return denormalized_time


# Add a button to trigger prediction
if st.button("Check when to send"):
    # Check if input is valid and calculate the normalized time
    try:
        normalized_time = normalize_time(time_input)
        
        # Load the dataset and perform predictions using the trained model
        with open(dataset_filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Prepare observation from dataset row
                observation = {
                    "time_of_day": np.array([float(row["time_of_day"])], dtype=np.float32),
                    "app_type": 0 if app_type == "Email" else 1,  # 0 for Email, 1 for WhatsApp
                    "location": int(row["location"]),
                    "activity": int(row["activity"])
                }

                # Predict action using the trained model
                action, _states = model.predict(observation, deterministic=True)
                
                if action == 1:  
                    current_time = denormalize_time(row["time_of_day"])
                    st.write(f"The notification should be sent at {current_time} (24-hour format).")
                    break  # Exit after first action, or continue based on logic

    except Exception as e:
        st.error(f"Error: {e}")

# import streamlit as st
# import numpy as np
# from stable_baselines3 import DQN
# import csv
# from stable_baselines3.common.logger import configure
# import datetime

# # Load the trained model
# model = DQN.load("./rl_agent/models/final")

# # Load the dataset
# dataset_filename = "./rl_agent/dataset_generation/user_behavior_dataset.csv"

# # Streamlit App
# st.title("Intelligent Notification Delivery System Demo")

# # Input: Time in 24-hour format
# time_input = st.text_input("Enter time in 24-hour format (HH:MM):", "14:30")

# # Input: App Type (Email or WhatsApp)
# app_type = st.selectbox("Select app type", ["Email", "WhatsApp"])

# # Normalize the time function
# def normalize_time(time_24hr):
#     hours, minutes = map(int, time_24hr.split(":"))
#     total_minutes = hours * 60 + minutes
#     normalized_value = total_minutes / 1440
#     return normalized_value

# # Check if input is valid and calculate the normalized time
# try:
#     normalized_time = normalize_time(time_input)
#     st.write(f"The normalized time for **{time_input}** is **{normalized_time:.6f}**")
    
#     # Load the dataset and perform predictions using the trained model
#     with open(dataset_filename, "r") as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             # Prepare observation from dataset row
#             observation = {
#                 "time_of_day": np.array([float(row["time_of_day"])], dtype=np.float32),
#                 "app_type": 0 if app_type == "Email" else 1,  
#                 "location": int(row["location"]),
#                 "activity": int(row["activity"])
#             }

#             # Predict action using the trained model
#             action, _states = model.predict(observation, deterministic=True)
            
#             if action == 1:
#                 current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 st.write(f"The user opened the notification at {current_time}.")
#                 break
                
# except Exception as e:
#     st.error(f"{e}")

# import streamlit as st

# def normalize_time(time_24hr):
#     """
#     Normalize a 24-hour time string (e.g., '14:30') to a value between 0 and 1.
    
#     Parameters:
#     time_24hr (str): A string representing the time in HH:MM format.
    
#     Returns:
#     float: The normalized time value between 0 and 1.
#     """
#     # Split the input time into hours and minutes
#     hours, minutes = map(int, time_24hr.split(":"))
    
#     # Convert the time to total minutes past midnight
#     total_minutes = hours * 60 + minutes
    
#     # Normalize by dividing by the total minutes in a day (1440)
#     normalized_value = total_minutes / 1440
    
#     return normalized_value

# # Streamlit App
# st.title("24-Hour Time Normalizer")

# # Input: Time in 24-hour format
# time_input = st.text_input("Enter time in 24-hour format (HH:MM):", "14:30")

# # Check if input is valid and calculate the normalized time
# try:
#     normalized = normalize_time(time_input)
#     st.write(f"The normalized time for **{time_input}** is **{normalized:.6f}**")
# except Exception as e:
#     st.error("Invalid time format! Please enter the time in HH:MM format.")

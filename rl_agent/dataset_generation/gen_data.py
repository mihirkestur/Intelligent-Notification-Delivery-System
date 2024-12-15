import numpy as np
import random
import csv

class SimulateUserBehavior:
    def __init__(self):
        self.time_of_day = 0.0

    def activity_encoding(self, activity):
        if activity == "still":
            return 2
        elif activity == "walking":
            return 1
        else:
            return 0

    def location_encoding(self, location):
        if location == "unknown":
            return 0
        elif location == "university":
            return 1
        elif location == "home":
            return 2
        else:
            return 3

    def simulate_state_of_env(self):
        done = self.time_of_day > 1
        if done:
            return None

        self.time_of_day += 1 / 1440.0  # Step size: 1/1440
        uni_arrival_time = 0.46
        library_arrival_time = 0.76
        home_return_time = 0.8333
        returned_home = False

        if self.time_of_day < 0.29167:  # Before 7 AM
            activity = self.activity_encoding("still")
            location = self.location_encoding("home")
        elif self.time_of_day < 0.45833:  # 7 AM - 11 AM
            activity = self.activity_encoding("still")
            location = self.location_encoding("home")
        elif self.time_of_day < 0.75:  # 11 AM - 6 PM
            if self.time_of_day < uni_arrival_time:
                activity = self.activity_encoding(random.choice(["walking", "running"]))
                location = self.location_encoding("unknown")
            else:
                location = self.location_encoding("university")
                if random.random() < 0.3:
                    activity = self.activity_encoding("walking")
                else:
                    activity = self.activity_encoding("still")
        elif self.time_of_day < home_return_time:  # 6 PM - 8 PM
            if self.time_of_day < library_arrival_time:
                activity = self.activity_encoding(random.choice(["walking", "running"]))
                location = self.location_encoding("unknown")
            else:
                location = self.location_encoding("library")
                if random.random() < 0.1:
                    activity = self.activity_encoding("walking")
                else:
                    activity = self.activity_encoding("still")
        elif self.time_of_day < 0.95833:  # 8 PM - 11 PM
            if not returned_home:
                if self.time_of_day < home_return_time + 0.0208:  # 30 minutes to return home
                    activity = self.activity_encoding(random.choice(["walking", "running"]))
                    location = self.location_encoding("unknown")
                else:
                    returned_home = True
                    activity = self.activity_encoding("still")
                    location = self.location_encoding("home")
            else:
                activity = self.activity_encoding("still")
                location = self.location_encoding("home")
        else:  # After 11 PM
            activity = self.activity_encoding("still")
            location = self.location_encoding("home")

        return {
            "time_of_day": round(self.time_of_day, 6),
            "location": location,
            "activity": activity,
        }


def generate_csv(filename):
    simulator = SimulateUserBehavior()
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["time_of_day", "location", "activity"])
        while simulator.time_of_day <= 1:
            state = simulator.simulate_state_of_env()
            if state:
                writer.writerow([state["time_of_day"], state["location"], state["activity"]])


# Generate the dataset
generate_csv("user_behavior_dataset.csv")

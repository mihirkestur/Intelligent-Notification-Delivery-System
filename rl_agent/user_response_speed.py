import random
from dataset_generation.generate import generate_human_readable_time
from stable_baselines3 import PPO, DDPG, DQN
import numpy as np

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
        if location == location_encoding("unknown") and activity == activity_encoding(
            "walking"
        ):
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


def generate_random_notifications():
    array_size = 10000
    result_array = [
        (random.uniform(0, 1), random.randint(0, 1)) for _ in range(array_size)
    ]
    return sorted(result_array, key=lambda x: x[0])


def get_average_accuracy_for_random(dataset: list[(float, int)]):
    model = DQN.load("./models/final")

    whatsapp_notifs = []
    email_notifs = []

    model_whatsapp_notifs = []
    model_email_notifs = []

    average = 0
    read = 0
    model_average = 0
    model_read = 0

    for v in dataset:
        norm_time, app = v
        if app == 0:
            whatsapp_notifs.append(norm_time)
        else:
            email_notifs.append(norm_time)

        env_state = simulate_state_of_env(norm_time)
        # observation = {
        #     "time_of_day": np.array([float(row["time_of_day"])], dtype=np.float32),
        #     "app_type": 1,
        #     "location": int(row["location"]),
        #     "activity": int(row["activity"])
        # }
        observation = {
            "time_of_day":  np.array([norm_time], dtype=np.float32),
            "location": env_state["location"],
            "app_type": app,
            "activity": env_state["activity"],
        }
        action, _states = model.predict(observation, deterministic=True)
        if action == 1:
            if app == 0:
                model_whatsapp_notifs.append(norm_time)
            else:
                model_email_notifs.append(norm_time)

        for test_app in range(2):
            data = {
                "time_of_day": norm_time,
                "location": env_state["location"],
                "app_type": test_app,
                "activity": env_state["activity"],
            }

            clicked = simulate_user(data)
            if clicked:
                if test_app == 0:
                    for whatsapp_time in whatsapp_notifs:
                        average += (norm_time - whatsapp_time) * 86400

                    read += len(whatsapp_notifs)
                    whatsapp_notifs = []

                    for whatsapp_time in model_whatsapp_notifs:
                        model_average += (norm_time - whatsapp_time) * 86400

                    model_read += len(model_whatsapp_notifs)
                    model_whatsapp_notifs = []

                else:
                    for email_time in email_notifs:
                        average += (norm_time - email_time) * 86400

                    read += len(email_notifs)
                    email_notifs = []

                    for email_time in model_email_notifs:
                        model_average += (norm_time - email_time) * 86400

                    model_read += len(model_email_notifs)
                    model_email_notifs = []

    print(f"Average time to click {average/read:.2f}s")
    print(f"Average time for model click {model_average/model_read:.2f}s")


def simulate_state_of_env(time_of_day):
    activity = None
    location = None
    uni_arrival_time = 0.46
    library_arrival_time = 0.76
    home_return_time = 0.8333
    returned_home = False

    def activity_encoding(walking_str) -> int:
        if walking_str == "still":
            return 2
        elif walking_str == "walking":
            return 1
        else:
            return 0

    def location_encoding(location_str) -> int:
        if location_str == "unknown":
            return 0
        elif location_str == "university":
            return 1
        elif location_str == "home":
            return 2
        else:
            return 3

    if time_of_day < 0.29167:  # Before 7 AM
        activity = activity_encoding("still")
        location = location_encoding("home")

    elif time_of_day < 0.45833:  # 7 AM - 11 AM
        activity = activity_encoding("still")
        location = location_encoding("home")

    elif time_of_day < 0.75:  # 11 AM - 6 PM
        if time_of_day < uni_arrival_time:
            activity = activity_encoding(random.choice(["walking", "running"]))
            location = location_encoding("unknown")
        else:
            location = location_encoding("university")
            if random.random() < 0.3:  # 30% chance to walk randomly
                activity = activity_encoding("walking")
            else:
                activity = activity_encoding("still")

    elif time_of_day < home_return_time:  # 6 PM - 8 PM
        if time_of_day < library_arrival_time:
            activity = activity_encoding(random.choice(["walking", "running"]))
            location = location_encoding("unknown")

        else:
            location = location_encoding("library")
            if random.random() < 0.1:  # 10% chance to walk randomly in library
                activity = activity_encoding("walking")
            else:
                activity = activity_encoding("still")

    elif time_of_day < 0.95833:  # 8 PM - 11 PM
        if not returned_home:
            if time_of_day < home_return_time + 0.0208:  # 30 minutes to return home
                activity = activity_encoding(random.choice(["walking", "running"]))
                location = location_encoding("unknown")
            else:
                returned_home = True
                activity = activity_encoding("still")
                location = location_encoding("home")
        else:
            activity = activity_encoding("still")
            location = location_encoding("home")

    else:  # After 11 PM
        activity = activity_encoding("still")
        location = location_encoding("home")

    return {
        "location": location,
        "activity": activity,
    }


if __name__ == "__main__":
    random.seed(134534)
    dataset = generate_random_notifications()
    get_average_accuracy_for_random(dataset)

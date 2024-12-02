import random
from main import simulate_user
from dataset_generation.generate import generate_human_readable_time


def generate_random_notifications():
    array_size = 10000
    result_array = [
        (random.uniform(0, 1), random.randint(0, 1)) for _ in range(array_size)
    ]
    return sorted(result_array, key=lambda x: x[0])


def get_average_accuracy_for_random(dataset: list[(float, int)]):
    whatsapp_notifs = []
    email_notifs = []

    for v in dataset:
        norm_time, app = v
        if app == 0:
            whatsapp_notifs.append(norm_time)
        else:
            email_notifs.append(norm_time)

        env_state = simulate_state_of_env(norm_time)
        data = {
            "time_of_day": norm_time,
            "location": env_state["location"],
            "app_type": app,
            "activity": env_state["activity"],
        }
        simulate_user(data)


def simulate_state_of_env(time_of_day):
    activity = None
    location = None
    
    def activity_encoding(self, walking_str) -> int:
        if walking_str == "still":
            return 2
        elif walking_str == "walking":
            return 1
        else:
            return 0

    def location_encoding(self, location_str) -> int:
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

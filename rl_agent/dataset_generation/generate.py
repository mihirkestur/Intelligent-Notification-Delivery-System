import pandas as pd
import numpy as np
import random

# Constants
NUM_ROWS = 1000
APP_NAMES = ['whatsapp', 'email']
ACTIVITIES = ['still', 'walking', 'running']

def generate_human_readable_time(normalized_time):
    total_minutes = normalized_time * 1440
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    
    period = 'AM' if hours < 12 else 'PM'
    hours = hours % 12
    hours = 12 if hours == 0 else hours
    
    return f'{hours}:{minutes:02d} {period}'

def generate_dataset():
    data = []
    arrived_at_uni = False
    arrived_at_library = False
    returned_home = False
    uni_arrival_time = random.uniform(0.45833, 0.5)  # Random time between 11 AM and 12 PM
    library_arrival_time = random.uniform(0.75, 0.7708)  # Random time between 6 PM and 6:30 PM
    home_return_time = 0.8333  # 8 PM

    for _ in range(NUM_ROWS):
        time_of_day = random.uniform(0, 1)
        human_readable_time = generate_human_readable_time(time_of_day)
        app_name = random.choice(APP_NAMES)
        
        if time_of_day < 0.29167:  # Before 7 AM
            activity = 'still'
            geofenced_location = 'home'
            clicked = 'no'
        elif time_of_day < 0.45833:  # 7 AM - 11 AM
            activity = 'still'
            geofenced_location = 'home'
            clicked = 'yes' if random.random() < (0.3 if app_name == 'whatsapp' else 0.9) else 'no'
        elif time_of_day < 0.75:  # 11 AM - 6 PM
            if time_of_day < uni_arrival_time:
                activity = random.choice(['walking', 'running'])
                geofenced_location = 'unknown'
            else:
                geofenced_location = 'university'
                if random.random() < 0.3:  # 30% chance to walk randomly
                    activity = 'walking'
                else:
                    activity = 'still'
            clicked = 'yes' if random.random() < 0.5 else 'no'
        elif time_of_day < home_return_time:  # 6 PM - 8 PM
            if time_of_day < library_arrival_time:
                activity = random.choice(['walking', 'running'])
                geofenced_location = 'unknown'
            
            else:
                geofenced_location = 'library'
                if random.random() < 0.1:  # 10% chance to walk randomly in library
                    activity = 'walking'
                else:
                    activity = 'still'
            clicked = 'yes' if random.random() < 0.5 else 'no'
        elif time_of_day < 0.95833:  # 8 PM - 11 PM
            if not returned_home:
                if time_of_day < home_return_time + 0.0208:  # 30 minutes to return home
                    activity = random.choice(['walking', 'running'])
                    geofenced_location = 'unknown'
                else:
                    returned_home = True
                    activity = 'still'
                    geofenced_location = 'home'
            else:
                activity = 'still'
                geofenced_location = 'home'
            clicked = 'yes' if random.random() < 0.7 else 'no'
        else:  # After 11 PM
            activity = 'still'
            geofenced_location = 'home'
            clicked = 'no'
        
        data.append([time_of_day, human_readable_time, app_name, activity, geofenced_location, clicked])
    
    return pd.DataFrame(data, columns=['time_of_day', 'human_readable_time', 'app_name', 'activity', 'geofenced_location', 'clicked'])

if __name__ == "__main__":
    # Generate the dataset
    dataset = generate_dataset()

    dataset.sort_values(by='time_of_day')[['time_of_day', 'human_readable_time', 'app_name', 'activity', 'geofenced_location']].to_csv('dataset.csv', index=False)
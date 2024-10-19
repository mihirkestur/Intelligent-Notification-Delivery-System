from stable_baselines3 import PPO, DDPG
from NotifRLEnv import NotificationTimingEnv
import numpy as np
# Create the environment
env = NotificationTimingEnv()

# # Train an RL agent
# model = DDPG("MultiInputPolicy", env, verbose=1)
# # model = PPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=1000)
# # Save the model
# model.save("./models/notification_model_xy_apps")


# Load the saved model
# model = PPO.load("./models/notification_model")
model = DDPG.load("./models/notification_model_xy_apps")
# Test the trained agent
observation = {
    "time_of_day": np.array([0.1], dtype=np.float32),
    "app_type": np.array([1], dtype=np.float32),
}
action, _states = model.predict(observation, deterministic=True)
print(action, _states)
# # obs, _ = env.reset()
# # env.send_notification_time = np.array([99])
# # obs, reward, done, truncated, info = env.step(action)
# # print(obs, reward)
# # env.render()
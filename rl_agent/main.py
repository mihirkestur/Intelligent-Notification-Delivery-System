from stable_baselines3 import PPO, DDPG, DQN
# from NotifRLEnv import NotificationTimingEnv
# from NotifRLEnvYN import NotificationTimingEnv
from BinNotif import NotificationTimingEnv
import numpy as np
# Create the environment
env = NotificationTimingEnv()

# # Train an RL agent
# model = DQN("MultiInputPolicy", env, verbose=1) # MultiInputPolicy
# # model = PPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=100000, log_interval=100)
# # Save the model
# model.save("./models/BinNotifTest4")


# Load the saved model
# model = PPO.load("./models/notification_model")
model = DQN.load("./models/BinNotifTest4")
# Test the trained agent
for i in range(1, 10):
    observation = {
        "time_of_day": np.array([i/10], dtype=np.float32),
        "app_type": np.array([0], dtype=np.float32),
    }
    action, _states = model.predict(observation, deterministic=True)
    print(action, _states)
# # obs, _ = env.reset()
# # env.send_notification_time = np.array([99])
# # obs, reward, done, truncated, info = env.step(action)
# # print(obs, reward)
# # env.render()
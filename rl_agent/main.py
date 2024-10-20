from stable_baselines3 import PPO, DDPG, DQN
# from NotifRLEnv import NotificationTimingEnv
# from NotifRLEnvYN import NotificationTimingEnv
from BinNotif import NotificationTimingEnv
import numpy as np
# Create the environment
env = NotificationTimingEnv()

# # Train an RL agent
# model = DQN("MlpPolicy", env, verbose=1) # MultiInputPolicy
# # model = PPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=10000)
# # Save the model
# model.save("./models/BinNotifTest3")


# Load the saved model
# model = PPO.load("./models/notification_model")
model = DQN.load("./models/BinNotifTest3")
# Test the trained agent
for i in range(0, 10):
    observation = {
        "time_of_day": np.array([0.5], dtype=np.float32),
        "app_type": np.array([1], dtype=np.float32),
    }
    action, _states = model.predict(np.array([i/10], dtype=np.float32), deterministic=True)
    print(action, _states)
# # obs, _ = env.reset()
# # env.send_notification_time = np.array([99])
# # obs, reward, done, truncated, info = env.step(action)
# # print(obs, reward)
# # env.render()
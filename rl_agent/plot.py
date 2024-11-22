import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv("./logs/progress.csv")

# Plot the episode rewards
plt.figure(figsize=(10, 5))
plt.plot(df['time/total_timesteps'], df['rollout/ep_rew_mean'])
plt.title('Episode Reward over Time')
plt.xlabel('Total Timesteps')
plt.ylabel('Mean Episode Reward')
plt.savefig('./plots/episode_reward_plot.png')
# plt.show()

# Plot the loss
plt.figure(figsize=(10, 5))
plt.plot(df['time/total_timesteps'], df['train/loss'])
plt.title('Training Loss over Time')
plt.xlabel('Total Timesteps')
plt.ylabel('Loss')
plt.savefig('./plots/training_loss_plot.png')
# plt.show()
import gym
from sb3_contrib import RecurrentPPO  # Use the contrib package for recurrent PPO
from snake_emotional_env import SnakeEmotionalEnv
import matplotlib.pyplot as plt

# Create and train the model with a recurrent policy
env = SnakeEmotionalEnv()
model = RecurrentPPO("MlpLstmPolicy", env, learning_rate=1e-4, verbose=1, n_steps=128, batch_size=32)
model.learn(total_timesteps=100_000)

# Test the trained model for one episode
obs = env.reset()
done = False

# Lists to store the emotion values at each timestep
fear_vals = []
joy_vals = []
sadness_vals = []

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()

    # Extract emotions from info dict
    current_emotions = info["emotions"]
    fear_vals.append(current_emotions["fear"])
    joy_vals.append(current_emotions["joy"])
    sadness_vals.append(current_emotions["sadness"])

env.close()

# Plot the emotions over time
plt.figure(figsize=(10, 6))
plt.plot(fear_vals, label='Fear')
plt.plot(joy_vals, label='Joy')
plt.plot(sadness_vals, label='Sadness')
plt.title("Emotional States over One Episode")
plt.xlabel("Timestep")
plt.ylabel("Emotion Intensity")
plt.legend()
plt.show()

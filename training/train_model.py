import pandas as pd
from stable_baselines3 import PPO
from env import TradingEnv

# Load Apple historical data
df = pd.read_csv("data/AAPL.csv")

# Create environment
env = TradingEnv(df)

# Create RL model
model = PPO("MlpPolicy", env, verbose=1)

# Train model (adjust steps later)
model.learn(total_timesteps=10_000)

# Save trained model
model.save("models/trained_model")
print("Model saved → models/trained_model.zip")

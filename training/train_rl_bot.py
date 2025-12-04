# training/train_rl_bot.py

import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from env import TradingEnv

# ----------------------------
# 1️⃣ Load Prepared Dataset
# ----------------------------
DATA_PATH = os.path.join("data", "prepared_AAPL.csv")
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"{DATA_PATH} not found. Please prepare your dataset first.")

df = pd.read_csv(DATA_PATH)
print(f"✅ Loaded dataset: {DATA_PATH}, shape: {df.shape}")

# ----------------------------
# 2️⃣ Create RL Environment
# ----------------------------
env = TradingEnv(df)

# ----------------------------
# 3️⃣ Create Model Directory
# ----------------------------
RL_MODELS_DIR = os.path.join("training", "models", "rl")
os.makedirs(RL_MODELS_DIR, exist_ok=True)
print(f"✅ RL models folder: {RL_MODELS_DIR}")

# ----------------------------
# 4️⃣ Setup Checkpoint Callback
# ----------------------------
checkpoint_callback = CheckpointCallback(
    save_freq=5000,                   # save every 5k steps
    save_path=RL_MODELS_DIR,
    name_prefix="ppo_aapl"
)

# ----------------------------
# 5️⃣ Initialize RL Model
# ----------------------------
model = PPO("MlpPolicy", env, verbose=1)

# ----------------------------
# 6️⃣ Start Training
# ----------------------------
TIMESTEPS = 50_000  # adjust as needed

print(f"🚀 Starting RL training for {TIMESTEPS} timesteps...")
model.learn(total_timesteps=TIMESTEPS, callback=checkpoint_callback)

# ----------------------------
# 7️⃣ Save Final Model
# ----------------------------
FINAL_MODEL_PATH = os.path.join(RL_MODELS_DIR, "ppo_aapl_final")
model.save(FINAL_MODEL_PATH)
print(f"🎉 RL training complete! Model saved at: {FINAL_MODEL_PATH}.zip")

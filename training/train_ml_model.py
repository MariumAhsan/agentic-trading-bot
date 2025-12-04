import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Try loading XGBoost if installed
try:
    from xgboost import XGBRegressor
    USE_XGB = True
except ImportError:
    print("⚠ XGBoost not installed. Skipping XGB model.")
    USE_XGB = False

# Create model directory if missing
os.makedirs("models/ml", exist_ok=True)

# -------------------------
# 1. LOAD PREPARED DATA
# -------------------------
import os

# Get project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT_DIR, "data", "prepared_AAPL.csv")

df = pd.read_csv(DATA_PATH)
print("✅ Loaded dataset from:", DATA_PATH)


# Drop NaN rows created by indicators
df.dropna(inplace=True)

# -------------------------
# 2. FEATURE SELECTION
# -------------------------
FEATURES = [
    "close", "high", "low", "open", "volume",
    "return", "ma_5", "ma_20", "ma_50",
    "rsi_14", "volatility_10"
]

TARGET = "future_return"

X = df[FEATURES]
y = df[TARGET]

# -------------------------
# 3. TRAIN / TEST SPLIT
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

# -------------------------
# 4. SCALING
# -------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save scaler
pd.DataFrame(scaler.mean_).to_csv("models/ml/scaler_mean.csv", index=False)
pd.DataFrame(scaler.scale_).to_csv("models/ml/scaler_scale.csv", index=False)

print("✓ Scaler saved")

# -------------------------
# 5. TRAIN MODELS
# -------------------------
results = {}

# Linear Regression
lin_model = LinearRegression()
lin_model.fit(X_train_scaled, y_train)
pred_lin = lin_model.predict(X_test_scaled)

results["LinearRegression"] = {
    "MAE": mean_absolute_error(y_test, pred_lin),
    "R2": r2_score(y_test, pred_lin)
}

# Save model
import joblib
joblib.dump(lin_model, "models/ml/linear_regression.pkl")


# Random Forest
rf = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)
rf.fit(X_train, y_train)   # RF does NOT need scaled data
pred_rf = rf.predict(X_test)

results["RandomForest"] = {
    "MAE": mean_absolute_error(y_test, pred_rf),
    "R2": r2_score(y_test, pred_rf)
}

joblib.dump(rf, "models/ml/random_forest.pkl")


# XGBoost (optional)
if USE_XGB:
    xgb = XGBRegressor(
        n_estimators=400,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        tree_method="hist"
    )

    xgb.fit(X_train, y_train)
    pred_xgb = xgb.predict(X_test)

    results["XGBoost"] = {
        "MAE": mean_absolute_error(y_test, pred_xgb),
        "R2": r2_score(y_test, pred_xgb)
    }

    joblib.dump(xgb, "models/ml/xgboost.pkl")

# -------------------------
# 6. PRINT RESULTS
# -------------------------
print("\n📊 MODEL PERFORMANCE:")
for model, metrics in results.items():
    print(f"\n--- {model} ---")
    print(f"MAE: {metrics['MAE']:.6f}")
    print(f"R2 : {metrics['R2']:.6f}")

print("\n🎉 ML models trained and saved in models/ml/")

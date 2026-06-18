import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score

print("Step 1: Loading dataset...")
df = pd.read_csv("data/train_transaction.csv")
print(f"Dataset loaded: {len(df)} rows")

print("Step 2: Loading feature names from XGBoost training...")
with open("models/artifacts/feature_names.pkl", "rb") as f:
    features = pickle.load(f)
print(f"Using same {len(features)} features for consistency")

X = df[features].copy()
y = df['isFraud'].copy()

print("Step 3: Encoding categorical columns...")
for col in X.select_dtypes(include='object').columns:
    le = LabelEncoder()
    X[col] = X[col].astype(str)
    X[col] = le.fit_transform(X[col])

print("Step 4: Filling missing values...")
X = X.fillna(-999)

print("Step 5: Training Isolation Forest...")
print("Isolation Forest learns what 'normal' looks like — no fraud labels needed.")
print("This will take 2-3 minutes...")

# Train on a sample for speed — Isolation Forest doesn't need all 590k rows
# It just needs enough to learn the normal distribution
sample_size = 100000
X_sample = X.sample(n=sample_size, random_state=42)

model_if = IsolationForest(
    n_estimators=100,
    contamination=0.035,   # ~3.5% fraud rate we saw in the data
    random_state=42,
    n_jobs=2,
    verbose=1
)

model_if.fit(X_sample)
print("Training complete.")

print("Step 6: Evaluating on full dataset...")
# decision_function returns anomaly score: more negative = more anomalous = more likely fraud
scores = model_if.decision_function(X)
# Flip sign so higher score = more fraudulent (consistent with XGBoost)
anomaly_scores = -scores

auc = roc_auc_score(y, anomaly_scores)
print(f"Isolation Forest AUC: {auc:.4f}")
print("(Lower AUC than XGBoost is expected — IF has no label info, it's unsupervised)")

print("Step 7: Saving model...")
with open("models/artifacts/isolation_forest_model.pkl", "wb") as f:
    pickle.dump(model_if, f)

print("Model saved to models/artifacts/isolation_forest_model.pkl")
print(f"\nDay 4 Step 2 complete. IF AUC: {auc:.4f}")
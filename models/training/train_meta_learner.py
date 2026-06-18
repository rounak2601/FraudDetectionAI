import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.preprocessing import LabelEncoder
import mlflow

print("Step 1: Loading dataset and models...")
df = pd.read_csv("data/train_transaction.csv")

with open("models/artifacts/feature_names.pkl", "rb") as f:
    features = pickle.load(f)

with open("models/artifacts/xgboost_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)

with open("models/artifacts/isolation_forest_model.pkl", "rb") as f:
    if_model = pickle.load(f)

print("All models loaded.")

print("Step 2: Preparing features...")
X = df[features].copy()
y = df['isFraud'].copy()

for col in X.select_dtypes(include='object').columns:
    le = LabelEncoder()
    X[col] = X[col].astype(str)
    X[col] = le.fit_transform(X[col])

X = X.fillna(-999)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Step 3: Generating scores from both base models...")
print("  Getting XGBoost probabilities...")
xgb_train_scores = xgb_model.predict_proba(X_train)[:, 1]
xgb_test_scores  = xgb_model.predict_proba(X_test)[:, 1]

print("  Getting Isolation Forest anomaly scores...")
if_train_scores = -if_model.decision_function(X_train)
if_test_scores  = -if_model.decision_function(X_test)

# Normalize IF scores to [0,1] range so they're on the same scale as XGBoost
def normalize(scores):
    mn, mx = scores.min(), scores.max()
    return (scores - mn) / (mx - mn + 1e-9)

if_train_scores = normalize(if_train_scores)
if_test_scores  = normalize(if_test_scores)

print("Step 4: Building meta-feature matrix...")
# The meta-learner sees: [xgb_score, if_score] → final fraud probability
meta_X_train = np.column_stack([xgb_train_scores, if_train_scores])
meta_X_test  = np.column_stack([xgb_test_scores,  if_test_scores])

print(f"Meta-feature matrix shape: {meta_X_train.shape}")
print(f"Sample row: XGBoost={meta_X_train[0,0]:.4f}, IF={meta_X_train[0,1]:.4f}")

print("Step 5: Training Meta-Learner (Logistic Regression)...")
with mlflow.start_run(run_name="meta_learner_v1"):
    meta_model = LogisticRegression(
        class_weight='balanced',
        random_state=42,
        max_iter=1000
    )
    meta_model.fit(meta_X_train, y_train)

    print("Step 6: Evaluating ensemble...")
    meta_proba = meta_model.predict_proba(meta_X_test)[:, 1]
    meta_auc   = roc_auc_score(y_test, meta_proba)

    # Compare all three
    xgb_auc = roc_auc_score(y_test, xgb_test_scores)
    if_auc  = roc_auc_score(y_test, if_test_scores)

    print(f"\n{'='*40}")
    print(f"  XGBoost alone:      AUC = {xgb_auc:.4f}")
    print(f"  Isolation Forest:   AUC = {if_auc:.4f}")
    print(f"  Ensemble (Meta):    AUC = {meta_auc:.4f}  ← final model")
    print(f"{'='*40}")

    # Check what the meta-learner learned
    coef = meta_model.coef_[0]
    print(f"\nMeta-learner weights:")
    print(f"  XGBoost weight:          {coef[0]:.4f}")
    print(f"  Isolation Forest weight: {coef[1]:.4f}")
    print("  (Higher = that model trusted more for final decision)")

    # Evaluate at a decision threshold
    threshold = 0.5
    y_pred = (meta_proba >= threshold).astype(int)
    print(f"\nClassification Report (threshold={threshold}):")
    print(classification_report(y_test, y_pred))

    mlflow.log_metric("ensemble_auc", meta_auc)
    mlflow.log_metric("xgb_auc", xgb_auc)
    mlflow.log_metric("if_auc", if_auc)
    mlflow.log_param("meta_model", "logistic_regression")

print("Step 7: Saving meta-learner...")
with open("models/artifacts/meta_learner.pkl", "wb") as f:
    pickle.dump(meta_model, f)

# Save normalization stats so inference pipeline can use them
if_stats = {
    "min": -if_model.decision_function(X).min(),
    "max": -if_model.decision_function(X).max()
}
with open("models/artifacts/if_normalization.pkl", "wb") as f:
    pickle.dump(if_stats, f)

print("Meta-learner saved to models/artifacts/meta_learner.pkl")
print(f"\nDay 4 Step 3 complete. Ensemble AUC: {meta_auc:.4f}")
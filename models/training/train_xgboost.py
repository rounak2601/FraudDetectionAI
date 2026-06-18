import pandas as pd
import numpy as np
import xgboost as xgb
import mlflow
import mlflow.xgboost
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.preprocessing import LabelEncoder

print("Step 1: Loading dataset...")
df = pd.read_csv("data/train_transaction.csv")
print(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")

print("Step 2: Selecting features...")
features = [
    'TransactionAmt',
    'ProductCD',
    'card4', 'card6',
    'P_emaildomain',
    'R_emaildomain',
    'addr1', 'addr2',
    'dist1',
    'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
    'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10'
]

target = 'isFraud'

# Keep only existing columns
features = [f for f in features if f in df.columns]
print(f"Using {len(features)} features")

X = df[features].copy()
y = df[target].copy()

print("Step 3: Encoding categorical columns...")
for col in X.select_dtypes(include='object').columns:
    le = LabelEncoder()
    X[col] = X[col].astype(str)
    X[col] = le.fit_transform(X[col])

print("Step 4: Filling missing values...")
X = X.fillna(-999)

print("Step 5: Splitting into train and test...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {len(X_train)} rows | Test: {len(X_test)} rows")
print(f"Fraud rate in train: {y_train.mean()*100:.2f}%")

fraud_count = (y_train == 0).sum()
non_fraud_count = (y_train == 1).sum()
scale_pos_weight = fraud_count / non_fraud_count
print(f"Class imbalance ratio: {scale_pos_weight:.1f}:1")

print("Step 6: Training XGBoost model...")
print("This will take 3-5 minutes on your machine...")

with mlflow.start_run(run_name="xgboost_fraud_v1"):
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        tree_method='hist',
        eval_metric='auc',
        random_state=42,
        n_jobs=2
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=10
    )

    print("Step 7: Evaluating model...")
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    print(f"\nAUC Score: {auc:.4f}")

    y_pred = model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    mlflow.log_metric("auc", auc)
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 6)

print("Step 8: Saving model...")
with open("models/artifacts/xgboost_model.pkl", "wb") as f:
    pickle.dump(model, f)

feature_names_path = "models/artifacts/feature_names.pkl"
with open(feature_names_path, "wb") as f:
    pickle.dump(features, f)

print("Model saved to models/artifacts/xgboost_model.pkl")
print("Feature names saved to models/artifacts/feature_names.pkl")
print(f"\nDay 4 Step 1 complete. AUC: {auc:.4f}")
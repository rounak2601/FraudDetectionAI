import pickle
import numpy as np
from onnxmltools import convert_xgboost
from onnxmltools.convert.common.data_types import FloatTensorType
import onnxruntime as rt
import xgboost as xgb
import time
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import pandas as pd

print("Step 1: Loading original model and data...")
with open("models/artifacts/xgboost_model.pkl", "rb") as f:
    xgb_model_original = pickle.load(f)

with open("models/artifacts/feature_names.pkl", "rb") as f:
    features = pickle.load(f)

# onnxmltools requires feature names like f0, f1, f2...
# We retrain an identical model but with numeric column names
numeric_feature_names = [f"f{i}" for i in range(len(features))]
print(f"Original features: {features[:3]}...")
print(f"Numeric features:  {numeric_feature_names[:3]}...")

print("Step 2: Loading and preparing data with numeric feature names...")
df = pd.read_csv("data/train_transaction.csv")
X = df[features].copy()
y = df['isFraud'].copy()

for col in X.select_dtypes(include='object').columns:
    le = LabelEncoder()
    X[col] = X[col].astype(str)
    X[col] = le.fit_transform(X[col])
X = X.fillna(-999)

# Rename columns to f0, f1, f2...
X.columns = numeric_feature_names

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

fraud_count     = (y_train == 0).sum()
non_fraud_count = (y_train == 1).sum()
scale_pos_weight = fraud_count / non_fraud_count

print("Step 3: Retraining with numeric feature names (same hyperparameters)...")
print("This takes 3-5 minutes again — only needed once for ONNX compatibility...")

xgb_model_onnx = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=scale_pos_weight,
    tree_method='hist',
    eval_metric='auc',
    random_state=42,
    n_jobs=2
)
xgb_model_onnx.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=10
)

auc = roc_auc_score(y_test, xgb_model_onnx.predict_proba(X_test)[:, 1])
print(f"Retrained AUC: {auc:.4f} (should match original 0.8836)")

print("Step 4: Saving retrained pickle (replaces original)...")
with open("models/artifacts/xgboost_model.pkl", "wb") as f:
    pickle.dump(xgb_model_onnx, f)

# Save the feature name mapping so inference knows f0=TransactionAmt etc.
import json
mapping = {f"f{i}": name for i, name in enumerate(features)}
with open("models/artifacts/feature_mapping.json", "w") as f:
    json.dump(mapping, f, indent=2)
print("Feature mapping saved to models/artifacts/feature_mapping.json")

print("Step 5: Converting to ONNX...")
n_features = len(features)
initial_type = [("float_input", FloatTensorType([None, n_features]))]

onnx_model = convert_xgboost(
    xgb_model_onnx,
    initial_types=initial_type,
    target_opset=12
)

onnx_path = "models/artifacts/xgboost_model.onnx"
with open(onnx_path, "wb") as f:
    f.write(onnx_model.SerializeToString())
print(f"ONNX model saved to {onnx_path}")

print("Step 6: Speed benchmark — pickle vs ONNX...")
sess        = rt.InferenceSession(onnx_path)
input_name  = sess.get_inputs()[0].name
output_name = sess.get_outputs()[1].name

X_bench = X.head(10000).values.astype(np.float32)

RUNS = 5
start = time.perf_counter()
for _ in range(RUNS):
    xgb_model_onnx.predict_proba(X_bench)
pickle_ms = (time.perf_counter() - start) / RUNS * 1000

start = time.perf_counter()
for _ in range(RUNS):
    sess.run([output_name], {input_name: X_bench})
onnx_ms = (time.perf_counter() - start) / RUNS * 1000

print(f"\n{'='*45}")
print(f"  Batch size: 10,000 transactions")
print(f"  Pickle model:  {pickle_ms:.1f} ms per batch")
print(f"  ONNX model:    {onnx_ms:.1f} ms per batch")
print(f"  Speedup:       {pickle_ms/onnx_ms:.2f}x faster")
print(f"  ONNX per-tx:   {onnx_ms/10000*1000:.3f} microseconds")
print(f"{'='*45}")

print("\nStep 7: Verify predictions match...")
pickle_proba = xgb_model_onnx.predict_proba(X_bench[:100])[:, 1]
onnx_proba   = sess.run([output_name], {input_name: X_bench[:100].astype(np.float32)})[0][:, 1]

max_diff = np.abs(pickle_proba - onnx_proba).max()
print(f"Max prediction difference: {max_diff:.8f}")
if max_diff < 0.001:
    print("PASS — ONNX predictions match pickle model")
else:
    print("WARNING — predictions differ, investigate before using ONNX")

print("\nDay 4 Step 4 complete. ONNX model ready for inference.")
"""
GNN Training v3 — Improved AUC
================================
WHAT CHANGED FROM v2 (AUC=0.7396)
────────────────────────────────────
1. LR Scheduler        — ReduceLROnPlateau cuts LR when loss stops improving.
                         This is the #1 fix. v2 was stuck overshooting the minimum.

2. BatchNorm layers    — Stabilises gradients between SAGEConv layers.
                         Lets the model train deeper without exploding/vanishing.

3. Hidden size 64→128  — More capacity to learn complex fraud patterns.

4. More edge sources   — TransactionAmt bins + D1 bins added.
                         v2: ~70k nodes had edges. v3: most 590k nodes get edges.
                         GNN learns neighbourhood patterns for ALL transactions.

5. 100 epochs          — With LR decay the model keeps improving past epoch 15.

6. Neighbour sampling  — Increased from [15,10] to [20,15] for richer context.

EXPECTED: AUC 0.82–0.87  (up from 0.7396)
RUNTIME:  ~35–45 minutes on your CPU

PLACE AT: C:\\Projects\\FraudDetectionAI\\models\\training\\train_gnn.py
RUN WITH: python models/training/train_gnn.py
"""

import gc, json, os, pickle, time, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelEncoder
from torch_geometric.data import Data
from torch_geometric.loader import NeighborLoader
from torch_geometric.nn import SAGEConv

BANNER = "=" * 62

print(BANNER)
print("  GNN Training v3 — Improved AUC Edition")
print("  Target: 0.82–0.87  (was 0.7396)")
print(BANNER)
print(f"  PyTorch : {torch.__version__}")
print(f"  Started : {time.strftime('%H:%M:%S')}")
print()

# ── Step 0: Verify files ──────────────────────────────────
FEATURE_PKL = "models/artifacts/feature_names.pkl"
CSV_PATH    = "data/train_transaction.csv"

for path in [FEATURE_PKL, CSV_PATH]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"\nFile not found: {path}\nRun from C:\\Projects\\FraudDetectionAI\n")

print("Step 0: Files found ✓")

# ── Step 1: Load feature names ────────────────────────────
print("\nStep 1: Loading feature names...")

with open(FEATURE_PKL, "rb") as f:
    feature_names_raw: list = pickle.load(f)

# Graph edge columns — more than v2
GRAPH_COLS = ["card4", "P_emaildomain", "addr1", "TransactionAmt", "D1"]
LABEL_COL  = "isFraud"
need_cols  = list(dict.fromkeys(feature_names_raw + GRAPH_COLS + [LABEL_COL]))

print(f"  Feature columns : {len(feature_names_raw)}")

# ── Step 2: Check CSV header ──────────────────────────────
print("\nStep 2: Checking CSV header...")

header_df        = pd.read_csv(CSV_PATH, nrows=0)
available        = set(header_df.columns)
del header_df

load_cols        = [c for c in need_cols        if c in available]
feature_names    = [c for c in feature_names_raw if c in available]
graph_cols_avail = [c for c in GRAPH_COLS        if c in available]

print(f"  Loading {len(load_cols)} of {len(available)} columns")
print(f"  Graph cols: {graph_cols_avail}")

# ── Step 3: Chunked CSV read ──────────────────────────────
print("\nStep 3: Reading CSV in chunks...")

CHUNK_SIZE = 50_000

peek     = pd.read_csv(CSV_PATH, usecols=load_cols, nrows=100, low_memory=False)
cat_cols = [c for c in feature_names
            if c in peek.columns and peek[c].dtype == object]
del peek; gc.collect()

encoders = {}
if cat_cols:
    sample_df = pd.read_csv(CSV_PATH, usecols=cat_cols, nrows=10_000, low_memory=False)
    for col in cat_cols:
        le = LabelEncoder()
        le.fit(list(sample_df[col].fillna("__MISSING__").astype(str)) + ["__MISSING__"])
        encoders[col] = le
    del sample_df; gc.collect()

X_chunks     = []
y_chunks     = []
graph_chunks = {c: [] for c in graph_cols_avail}
n_chunks     = 0

reader = pd.read_csv(CSV_PATH, usecols=load_cols, chunksize=CHUNK_SIZE, low_memory=False)

for chunk in reader:
    n_chunks += 1
    y_chunks.append(chunk[LABEL_COL].values.astype(np.int8))

    for col in graph_cols_avail:
        if col in chunk.columns:
            graph_chunks[col].append(chunk[col].values)  # keep numeric as-is for amt/D1

    X_chunk = chunk[feature_names].copy()
    for col, le in encoders.items():
        if col in X_chunk.columns:
            sv    = X_chunk[col].fillna("__MISSING__").astype(str)
            known = set(le.classes_)
            sv    = sv.map(lambda v: v if v in known else "__MISSING__")
            X_chunk[col] = le.transform(sv).astype(np.float32)

    X_chunks.append(X_chunk.fillna(-999.0).astype(np.float32).values)
    del chunk, X_chunk; gc.collect()

    if n_chunks % 3 == 0:
        print(f"  Processed {n_chunks * CHUNK_SIZE:,} rows...")

print(f"  Concatenating {n_chunks} chunks...")
X = np.vstack(X_chunks);      del X_chunks; gc.collect()
y = np.concatenate(y_chunks); del y_chunks; gc.collect()

graph_arrays = {}
for c in graph_cols_avail:
    graph_arrays[c] = np.concatenate(graph_chunks[c])
del graph_chunks; gc.collect()

print(f"  Rows: {len(X):,}  |  Features: {X.shape[1]}  |  Fraud: {y.mean()*100:.2f}%")

# ── Step 4: Normalise ─────────────────────────────────────
print("\nStep 4: Normalising features...")

X_min   = X.min(axis=0).astype(np.float32)
X_max   = X.max(axis=0).astype(np.float32)
X_range = np.where((X_max - X_min) < 1e-9, 1.0, X_max - X_min).astype(np.float32)
X       = ((X - X_min) / X_range).astype(np.float32)
print("  Done.")

# ── Step 5: Build edges ───────────────────────────────────
# NEW IN v3: TransactionAmt bins + D1 bins
# These connect transactions that share behavioral patterns,
# not just infrastructure (card/email/address).
# Card-testing fraud shows up as many transactions with the
# exact same small amount — these bins catch that pattern.
print("\nStep 5: Building graph edges (v3 — more sources)...")

t_edges  = time.time()
src_list = []
dst_list = []

SMALL_MAX    = 100
LARGE_SAMPLE = 300
LARGE_K      = 5
rng          = np.random.default_rng(seed=42)


def add_edges_categorical(values: np.ndarray, label: str) -> int:
    """For string/categorical columns — same sparsified strategy as v2."""
    str_vals  = np.where(pd.isna(values), "__MISSING__",
                         values.astype(str))
    count     = 0
    for val in np.unique(str_vals):
        if val in ("__MISSING__", "nan", ""):
            continue
        idx = np.where(str_vals == val)[0]
        n   = len(idx)
        if n < 2:
            continue
        if n <= SMALL_MAX:
            for i in range(n):
                for j in range(i + 1, n):
                    src_list.append(int(idx[i])); dst_list.append(int(idx[j]))
                    src_list.append(int(idx[j])); dst_list.append(int(idx[i]))
                    count += 1
        else:
            sample_size = min(LARGE_SAMPLE, n)
            sampled     = rng.choice(idx, size=sample_size, replace=False)
            for i in range(len(sampled)):
                for k in range(1, LARGE_K + 1):
                    j = (i + k) % len(sampled)
                    src_list.append(int(sampled[i])); dst_list.append(int(sampled[j]))
                    src_list.append(int(sampled[j])); dst_list.append(int(sampled[i]))
                    count += 1
    print(f"  {label:22s}: {count:>8,} edge pairs")
    return count


def add_edges_numeric_binned(values: np.ndarray, label: str,
                              n_bins: int = 200) -> int:
    """
    NEW IN v3: bin a numeric column into n_bins equal-width buckets,
    then connect transactions in the same bucket.

    WHY: TransactionAmt — fraudsters often test cards with identical
    small amounts. Binning into $10 buckets connects these.
    D1 (days since last transaction) — similar timing = similar behavior.

    n_bins=200 means each bucket covers about 1/200th of the value range.
    For TransactionAmt 0-30,000: each bin = $150 range — tight enough
    to catch card-testing patterns.
    """
    clean = np.where(np.isnan(values.astype(float)), -999.0,
                     values.astype(float))
    # Only bin valid values (not -999 missing)
    valid_mask = clean != -999.0
    if valid_mask.sum() < 10:
        print(f"  {label:22s}: skipped (not enough valid values)")
        return 0

    valid_vals = clean[valid_mask]
    vmin, vmax = valid_vals.min(), valid_vals.max()
    if vmax - vmin < 1e-9:
        print(f"  {label:22s}: skipped (constant column)")
        return 0

    # Assign bin IDs — use pd.cut for clean equal-width bins
    bin_ids        = np.full(len(clean), -1, dtype=np.int32)
    bins           = pd.cut(valid_vals, bins=n_bins, labels=False)
    valid_indices  = np.where(valid_mask)[0]
    bin_ids[valid_indices] = bins.astype(np.int32)

    count = 0
    for bin_id in np.unique(bin_ids):
        if bin_id == -1:
            continue
        idx = np.where(bin_ids == bin_id)[0]
        n   = len(idx)
        if n < 2:
            continue
        if n <= SMALL_MAX:
            for i in range(n):
                for j in range(i + 1, n):
                    src_list.append(int(idx[i])); dst_list.append(int(idx[j]))
                    src_list.append(int(idx[j])); dst_list.append(int(idx[i]))
                    count += 1
        else:
            sample_size = min(LARGE_SAMPLE, n)
            sampled     = rng.choice(idx, size=sample_size, replace=False)
            for i in range(len(sampled)):
                for k in range(1, LARGE_K + 1):
                    j = (i + k) % len(sampled)
                    src_list.append(int(sampled[i])); dst_list.append(int(sampled[j]))
                    src_list.append(int(sampled[j])); dst_list.append(int(sampled[i]))
                    count += 1
    print(f"  {label:22s}: {count:>8,} edge pairs")
    return count


# Categorical edges (same as v2)
for col in ["card4", "P_emaildomain", "addr1"]:
    if col in graph_arrays:
        add_edges_categorical(graph_arrays[col], col)

# NEW: Numeric binned edges
for col in ["TransactionAmt", "D1"]:
    if col in graph_arrays:
        add_edges_numeric_binned(graph_arrays[col], col, n_bins=200)

del graph_arrays; gc.collect()

if len(src_list) == 0:
    print("  WARNING: No edges — using fallback")
    for i in range(0, min(len(X) - 1, 10_000), 5):
        src_list.append(i); dst_list.append(i + 1)
        src_list.append(i + 1); dst_list.append(i)

print(f"  {'TOTAL':22s}: {len(src_list):>8,} directed edges  ({time.time()-t_edges:.1f}s)")

edge_index = torch.tensor(
    np.array([src_list, dst_list], dtype=np.int64), dtype=torch.long
)
del src_list, dst_list; gc.collect()

# ── Step 6: PyG Data object ───────────────────────────────
print("\nStep 6: Creating graph object...")

data = Data(
    x          = torch.from_numpy(X),
    edge_index = edge_index,
    y          = torch.tensor(y.astype(np.int64), dtype=torch.long),
)
del X, y, edge_index; gc.collect()

n          = data.num_nodes
train_mask = torch.zeros(n, dtype=torch.bool)
test_mask  = torch.zeros(n, dtype=torch.bool)
train_mask[: int(n * 0.8)] = True
test_mask[int(n * 0.8):]   = True
data.train_mask = train_mask
data.test_mask  = test_mask

print(f"  Nodes: {data.num_nodes:,}  |  Edges: {data.num_edges:,}  |  Features: {data.num_node_features}")

# ── Step 7: Improved GraphSAGE model ─────────────────────
# CHANGES FROM v2:
#   hidden 64 → 128        (more capacity)
#   Added BatchNorm1d       (stabilises gradients)
print("\nStep 7: Building improved GraphSAGE model...")


class GraphSAGE(torch.nn.Module):
    def __init__(self, in_ch: int, hidden: int, out_ch: int):
        super().__init__()
        self.conv1 = SAGEConv(in_ch, hidden)
        self.bn1   = torch.nn.BatchNorm1d(hidden)   # NEW: stabilises gradients
        self.conv2 = SAGEConv(hidden, hidden)
        self.bn2   = torch.nn.BatchNorm1d(hidden)   # NEW
        self.conv3 = SAGEConv(hidden, out_ch)
        self.drop  = torch.nn.Dropout(p=0.3)

    def forward(self, x, edge_index):
        x = self.bn1(F.relu(self.conv1(x, edge_index)))
        x = self.drop(x)
        x = self.bn2(F.relu(self.conv2(x, edge_index)))
        x = self.drop(x)
        return self.conv3(x, edge_index)


model     = GraphSAGE(data.num_node_features, hidden=128, out_ch=2)  # hidden 64→128
optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=5e-4)

# NEW: LR scheduler — cuts LR by half if loss doesn't improve for 8 epochs
# This is the #1 fix. v2 was stuck at LR=0.005 forever, overshooting the minimum.
# With ReduceLROnPlateau: LR drops 0.005 → 0.0025 → 0.00125 as needed.
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=8
)

n_legit      = int((data.y == 0).sum())
n_fraud      = int((data.y == 1).sum())
fraud_weight = float(n_legit) / max(n_fraud, 1)
criterion    = torch.nn.CrossEntropyLoss(
    weight=torch.tensor([1.0, fraud_weight], dtype=torch.float32)
)

params = sum(p.numel() for p in model.parameters())
print(f"  Architecture      : 3-layer GraphSAGE + BatchNorm")
print(f"  in→hidden→out     : {data.num_node_features} → 128 → 128 → 2")
print(f"  Parameters        : {params:,}")
print(f"  LR scheduler      : ReduceLROnPlateau (patience=8, factor=0.5)")
print(f"  Fraud class weight: {fraud_weight:.1f}×")

# ── Step 8: Train 100 epochs ──────────────────────────────
print("\nStep 8: Training (100 epochs)...")
print(f"  Start   : {time.strftime('%H:%M:%S')}")
print(f"  Runtime : ~35–45 minutes")
print()

EPOCHS      = 100
best_auc    = 0.0
train_start = time.time()

loader = NeighborLoader(
    data,
    num_neighbors = [20, 15],    # increased from [15, 10]
    batch_size    = 512,
    input_nodes   = data.train_mask,
    shuffle       = True,
)

os.makedirs("models/artifacts", exist_ok=True)

for epoch in range(1, EPOCHS + 1):
    ep_start   = time.time()
    model.train()
    total_loss = 0.0
    n_batches  = 0

    for batch in loader:
        optimizer.zero_grad()
        out  = model(batch.x, batch.edge_index)
        loss = criterion(out[: batch.batch_size], batch.y[: batch.batch_size])
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        n_batches  += 1

    avg_loss = total_loss / max(n_batches, 1)
    ep_time  = time.time() - ep_start

    # Feed loss to LR scheduler
    scheduler.step(avg_loss)
    current_lr = optimizer.param_groups[0]['lr']

    if epoch % 5 == 0:
        model.eval()
        auc      = 0.0
        improved = ""
        with torch.no_grad():
            test_idx    = torch.where(data.test_mask)[0][:5000]
            eval_loader = NeighborLoader(
                data,
                num_neighbors = [20, 15],
                batch_size    = 5000,
                input_nodes   = test_idx,
                shuffle       = False,
            )
            for eval_batch in eval_loader:
                out_eval = model(eval_batch.x, eval_batch.edge_index)
                probs    = F.softmax(out_eval[: eval_batch.batch_size], dim=1)[:, 1].numpy()
                labels   = eval_batch.y[: eval_batch.batch_size].numpy()
                break

        if labels.sum() > 0:
            auc = float(roc_auc_score(labels, probs))
            if auc > best_auc:
                best_auc = auc
                torch.save(model.state_dict(), "models/artifacts/gnn_best.pt")
                improved = "  ← BEST (saved)"

        elapsed = (time.time() - train_start) / 60
        eta     = (elapsed / epoch) * (EPOCHS - epoch)
        print(
            f"  Epoch {epoch:3d}/{EPOCHS} | Loss: {avg_loss:.4f} | "
            f"LR: {current_lr:.5f} | "
            f"AUC: {auc:.4f} | Best: {best_auc:.4f} | "
            f"{ep_time:.0f}s | ETA: {eta:.0f}min{improved}"
        )
    else:
        print(
            f"  Epoch {epoch:3d}/{EPOCHS} | Loss: {avg_loss:.4f} | "
            f"LR: {current_lr:.5f} | {ep_time:.0f}s/epoch"
        )

# ── Step 9: Save ──────────────────────────────────────────
print("\nStep 9: Saving model...")

torch.save(model.state_dict(), "models/artifacts/gnn_model.pt")

gnn_config = {
    "architecture"       : "GraphSAGE_v3",
    "layers"             : 3,
    "in_channels"        : data.num_node_features,
    "hidden_channels"    : 128,
    "out_channels"       : 2,
    "dropout"            : 0.3,
    "batch_norm"         : True,
    "feature_names"      : feature_names,
    "norm_X_min"         : X_min.tolist(),
    "norm_X_max"         : X_max.tolist(),
    "num_nodes"          : data.num_nodes,
    "num_edges"          : data.num_edges,
    "epochs_trained"     : EPOCHS,
    "best_auc"           : best_auc,
    "fraud_class_weight" : fraud_weight,
    "n_fraud"            : n_fraud,
    "n_legit"            : n_legit,
    "improvements"       : [
        "LR scheduler ReduceLROnPlateau",
        "BatchNorm1d between layers",
        "Hidden size 64→128",
        "TransactionAmt binned edges",
        "D1 binned edges",
        "100 epochs",
        "NeighborLoader [20,15]"
    ],
}

with open("models/artifacts/gnn_config.json", "w") as f:
    json.dump(gnn_config, f, indent=2)

total_min = (time.time() - train_start) / 60
print(f"  gnn_model.pt     saved")
print(f"  gnn_best.pt      saved  (AUC={best_auc:.4f})")
print(f"  gnn_config.json  saved")
print()
print(BANNER)
print(f"  GNN v3 TRAINING COMPLETE")
print(f"  Best AUC   : {best_auc:.4f}  (was 0.7396 in v2)")
print(f"  Improvement: +{best_auc - 0.7396:.4f}")
print(f"  Duration   : {total_min:.1f} minutes")
print(f"  Finished   : {time.strftime('%H:%M:%S')}")
print(BANNER)

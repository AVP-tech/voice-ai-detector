import os
import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import GroupShuffleSplit

from features.extract import extract_features_from_wav

# 🔒 FINAL DATA DIRECTORIES (LOCK THESE)
AI_DIR = "data/ai_processed_v2"
HUMAN_DIR = "data/human_processed_v2"

X = []
y = []
groups = []  # group = original file (prevents leakage)


def load_folder(folder, label):
    for file in os.listdir(folder):
        if not file.endswith(".wav"):
            continue

        path = os.path.join(folder, file)
        feats = extract_features_from_wav(path)

        if feats is None:
            continue

        X.append(feats)
        y.append(label)

        # 🔑 GROUP ID = original audio source
        # removes segment-level leakage
        base_id = file.split("_call")[0]
        groups.append(base_id)


print("Loading AI audio...")
load_folder(AI_DIR, 1)

print("Loading Human audio...")
load_folder(HUMAN_DIR, 0)

X = np.array(X)
y = np.array(y)
groups = np.array(groups)

print(f"Total segments: {len(X)}")
print(f"Feature length: {X.shape[1]}")

# 🔥 GROUP-AWARE SPLIT (MOST IMPORTANT PART)
gss = GroupShuffleSplit(
    n_splits=1,
    test_size=0.3,
    random_state=42
)

train_idx, test_idx = next(gss.split(X, y, groups))

X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

# Base model
base_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42
)

# 🔥 CALIBRATED MODEL
model = CalibratedClassifierCV(
    base_model,
    method="sigmoid",
    cv=5
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# Save final calibrated + leakage-safe model
os.makedirs("artifacts", exist_ok=True)
joblib.dump(model, "artifacts/model.pkl")

print("\n✅ Final calibrated, group-safe model saved at artifacts/model.pkl")

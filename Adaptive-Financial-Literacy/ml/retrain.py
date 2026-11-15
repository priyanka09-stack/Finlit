import json
import os
import shutil
import sys

import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from pymongo import MongoClient
from tensorflow import keras

HERE = os.path.dirname(__file__)
load_dotenv(os.path.join(HERE, "..", "backend", ".env"))

MIN_REAL = int(sys.argv[1]) if len(sys.argv) > 1 else 50   # test ke liye: python retrain.py 10
REAL_WEIGHT = 5.0
FEATURES = ["topic_mastery", "avg_mastery", "difficulty", "past_pass_rate", "experience", "progress"]
MODEL_FILE = os.path.join(HERE, "model.keras")
WEIGHTS_FILE = os.path.join(HERE, "..", "backend", "model_weights.json")

np.random.seed(7)
tf.random.set_seed(7)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def make_dataset(n):
    """train_model.py wala synthetic generator (pretraining data)."""
    topic = np.random.beta(2, 2, n)
    avg = np.clip(topic + np.random.normal(0, 0.15, n), 0, 1)
    past = np.clip(0.1 + 0.8 * avg + np.random.normal(0, 0.15, n), 0, 1)
    experience = np.random.uniform(0, 1, n)
    progress = np.clip(0.8 * experience + np.random.normal(0, 0.1, n), 0, 1)
    difficulty = np.random.choice([0.0, 0.5, 1.0], n)
    required = np.where(difficulty == 0.0, 0.25, np.where(difficulty == 0.5, 0.5, 0.75))
    skill = 0.55 * topic + 0.25 * avg + 0.10 * past + 0.05 * experience + 0.05 * progress
    logit = 7 * (skill - required) + np.random.normal(0, 0.5, n)
    passed = (np.random.rand(n) < sigmoid(logit)).astype(np.float32)
    X = np.column_stack([topic, avg, difficulty, past, experience, progress]).astype(np.float32)
    return X, passed


def load_real():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME")]
    rows = list(db.attempts.find(
        {"features": {"$exists": True}, "passed": {"$exists": True}},
        {"features": 1, "passed": 1},
    ))
    if not rows:
        return np.empty((0, len(FEATURES)), dtype=np.float32), np.empty((0,), dtype=np.float32)
    X = np.array([r["features"] for r in rows], dtype=np.float32)
    y = np.array([1.0 if r["passed"] else 0.0 for r in rows], dtype=np.float32)
    return X, y


# ---------- 1. Real data check ----------
X_real, y_real = load_real()
n_real = len(X_real)
needed = max(MIN_REAL, 10)
print(f"Real attempts with logged features: {n_real}")
if n_real < needed:
    print(f"Need at least {needed} to retrain safely. Keeping the current model.")
    sys.exit(0)

# ---------- 2. Split: real data ka hissa test ke liye alag ----------
perm = np.random.permutation(n_real)
X_real, y_real = X_real[perm], y_real[perm]
n_test = max(5, int(0.2 * n_real))
X_rt, y_rt = X_real[:n_test], y_real[:n_test]
X_rtrain, y_rtrain = X_real[n_test:], y_real[n_test:]

X_syn, y_syn = make_dataset(3000)
X = np.vstack([X_syn, X_rtrain])
y = np.concatenate([y_syn, y_rtrain])
w = np.concatenate([np.ones(len(X_syn)), np.full(len(X_rtrain), REAL_WEIGHT)]).astype(np.float32)
shuffle = np.random.permutation(len(X))
X, y, w = X[shuffle], y[shuffle], w[shuffle]
print(f"Training on {len(X_syn)} synthetic + {len(X_rtrain)} real (weight {REAL_WEIGHT}); testing on {len(X_rt)} real")

# ---------- 3. Fine-tune ----------
old = keras.models.load_model(MODEL_FILE)
new = keras.models.load_model(MODEL_FILE)
new.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0005),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)
stop = keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True)
new.fit(X, y, sample_weight=w, validation_split=0.1, epochs=30, batch_size=64, callbacks=[stop], verbose=2)

# ---------- 4. Champion vs challenger (real held-out data pe) ----------
old_res = old.evaluate(X_rt, y_rt, verbose=0, return_dict=True)
new_res = new.evaluate(X_rt, y_rt, verbose=0, return_dict=True)
print("\nOn held-out REAL attempts:")
print(f"  old model: loss {old_res['loss']:.4f}  accuracy {old_res['accuracy']:.3f}")
print(f"  new model: loss {new_res['loss']:.4f}  accuracy {new_res['accuracy']:.3f}")

if new_res["loss"] > old_res["loss"]:
    print("\nNew model is not better. Keeping the current model (nothing changed).")
    sys.exit(0)

# ---------- 5. Promote: backup + export ----------
shutil.copy(MODEL_FILE, os.path.join(HERE, "model_previous.keras"))
if os.path.exists(WEIGHTS_FILE):
    shutil.copy(WEIGHTS_FILE, os.path.join(HERE, "model_weights_previous.json"))

activations = ["relu", "relu", "sigmoid"]
dense_layers = [l for l in new.layers if l.get_weights()]
layers = []
for layer, act in zip(dense_layers, activations):
    W, b = layer.get_weights()
    layers.append({"W": W.tolist(), "b": b.tolist(), "activation": act})

baseline = max(float(y_rt.mean()), 1 - float(y_rt.mean()))
meta = {
    "features": FEATURES,
    "trained_on": f"synthetic + {n_real} real attempts",
    "n_samples": int(len(X)),
    "test_accuracy": round(float(new_res["accuracy"]), 4),
    "test_auc": None,
    "baseline_accuracy": round(baseline, 4),
    "evaluated_on": f"{len(X_rt)} held-out real attempts",
    "tensorflow_version": tf.__version__,
}
with open(WEIGHTS_FILE, "w") as f:
    json.dump({"meta": meta, "layers": layers}, f)
new.save(MODEL_FILE)

print("\nNew model saved. Old one backed up as ml/model_previous.keras.")
print("IMPORTANT: restart the Flask backend so it loads the new weights.")
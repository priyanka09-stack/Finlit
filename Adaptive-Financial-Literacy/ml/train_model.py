import json
import os

import numpy as np
import tensorflow as tf
from tensorflow import keras

SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)

FEATURES = ["topic_mastery", "avg_mastery", "difficulty", "past_pass_rate", "experience", "progress"]
HERE = os.path.dirname(__file__)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# ---------- 1. Synthetic dataset ----------
def make_dataset(n=6000):
    topic = np.random.beta(2, 2, n)
    avg = np.clip(topic + np.random.normal(0, 0.15, n), 0, 1)
    past = np.clip(0.1 + 0.8 * avg + np.random.normal(0, 0.15, n), 0, 1)
    experience = np.random.uniform(0, 1, n)
    progress = np.clip(0.8 * experience + np.random.normal(0, 0.1, n), 0, 1)
    difficulty = np.random.choice([0.0, 0.5, 1.0], n)

    # module ko pass karne ke liye kitni mastery chahiye
    required = np.where(difficulty == 0.0, 0.25, np.where(difficulty == 0.5, 0.5, 0.75))
    skill = 0.55 * topic + 0.25 * avg + 0.10 * past + 0.05 * experience + 0.05 * progress

    logit = 7 * (skill - required) + np.random.normal(0, 0.5, n)
    passed = (np.random.rand(n) < sigmoid(logit)).astype(np.float32)

    X = np.column_stack([topic, avg, difficulty, past, experience, progress]).astype(np.float32)
    return X, passed


X, y = make_dataset()
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]
print(f"Samples: {len(X)}  (train {len(X_train)}, test {len(X_test)})  pass rate: {y.mean():.2f}")

# ---------- 2. Model ----------
model = keras.Sequential([
    keras.layers.Input(shape=(len(FEATURES),)),
    keras.layers.Dense(16, activation="relu"),
    keras.layers.Dense(8, activation="relu"),
    keras.layers.Dense(1, activation="sigmoid"),
])
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy", keras.metrics.AUC(name="auc")],
)
model.summary()

# ---------- 3. Training ----------
stop = keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
model.fit(
    X_train, y_train,
    validation_split=0.2, epochs=60, batch_size=64,
    callbacks=[stop], verbose=2,
)

# ---------- 4. Evaluation (test data jo model ne kabhi nahi dekha) ----------
loss, acc, auc = model.evaluate(X_test, y_test, verbose=0)
baseline = max(y_test.mean(), 1 - y_test.mean())
print(f"\nTest accuracy: {acc:.3f}   (baseline, hamesha ek hi jawab dene wala: {baseline:.3f})")
print(f"Test AUC     : {auc:.3f}")

# ---------- 5. Demo: alag students, alag difficulty ----------
students = {
    "weak student   ": (0.2, 0.3, 0.3),
    "average student": (0.5, 0.5, 0.5),
    "strong student ": (0.85, 0.8, 0.8),
}
print("\nPredicted pass probability (easy / medium / hard):")
for name, (topic, avg, past) in students.items():
    rows = np.array([[topic, avg, d, past, 0.5, 0.4] for d in (0.0, 0.5, 1.0)], dtype=np.float32)
    p = model.predict(rows, verbose=0).flatten()
    print(f"  {name}: {p[0]:.2f} / {p[1]:.2f} / {p[2]:.2f}")

# ---------- 6. Weights export (backend numpy se chalayega, TensorFlow ki zaroorat nahi) ----------
activations = ["relu", "relu", "sigmoid"]
dense_layers = [l for l in model.layers if l.get_weights()]
layers = []
for layer, act in zip(dense_layers, activations):
    W, b = layer.get_weights()
    layers.append({"W": W.tolist(), "b": b.tolist(), "activation": act})


def numpy_predict(x, layers):
    a = x
    for layer in layers:
        z = a @ np.array(layer["W"]) + np.array(layer["b"])
        a = np.maximum(z, 0) if layer["activation"] == "relu" else sigmoid(z)
    return a


# export sahi hai ya nahi, ye check
sample = X_test[:5]
diff = np.abs(model.predict(sample, verbose=0).flatten() - numpy_predict(sample, layers).flatten()).max()
print(f"\nKeras vs numpy max difference: {diff:.8f}  (bahut chhota hona chahiye)")

meta = {
    "features": FEATURES,
    "trained_on": "synthetic simulated students",
    "n_samples": int(len(X)),
    "test_accuracy": round(float(acc), 4),
    "test_auc": round(float(auc), 4),
    "baseline_accuracy": round(float(baseline), 4),
    "tensorflow_version": tf.__version__,
}

out_path = os.path.join(HERE, "..", "backend", "model_weights.json")
with open(out_path, "w") as f:
    json.dump({"meta": meta, "layers": layers}, f)
model.save(os.path.join(HERE, "model.keras"))
print(f"\nSaved: {os.path.abspath(out_path)}")
print("Saved: ml/model.keras")
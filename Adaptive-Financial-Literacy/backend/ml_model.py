import json
import math
import os

_PATH = os.path.join(os.path.dirname(__file__), "model_weights.json")
DIFFICULTY = {"easy": 0.0, "medium": 0.5, "hard": 1.0}

try:
    with open(_PATH) as f:
        _MODEL = json.load(f)
except Exception:
    _MODEL = None
    print("WARNING: model_weights.json not found, using rule-based path only")


def model_available():
    return _MODEL is not None


def model_info():
    return _MODEL["meta"] if _MODEL else None


def _sigmoid(x):
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    z = math.exp(x)
    return z / (1 + z)


def predict_pass_probability(features):
    """6 features -> pass probability (0 se 1). Keras model ka forward pass, bina TensorFlow ke."""
    if _MODEL is None:
        return None
    a = features
    for layer in _MODEL["layers"]:
        W, b = layer["W"], layer["b"]
        out = []
        for j in range(len(b)):
            z = b[j] + sum(a[i] * W[i][j] for i in range(len(a)))
            out.append(max(0.0, z) if layer["activation"] == "relu" else _sigmoid(z))
        a = out
    return a[0]


def build_features(student, module, attempt_count, past_pass_rate, total_modules):
    """Order wahi hai jo training mein tha: topic, avg, difficulty, past_pass, experience, progress."""
    scores = student.get("topic_scores", {})
    percents = [v["percent"] for v in scores.values() if "percent" in v]
    topic = scores.get(module["topic"], {}).get("percent", 50) / 100
    avg = (sum(percents) / len(percents) / 100) if percents else 0.0
    completed = len(student.get("completed_modules", []))
    return [
        topic,
        avg,
        DIFFICULTY[module["difficulty"]],
        past_pass_rate,
        min(attempt_count, 10) / 10,
        completed / max(total_modules, 1),
    ]
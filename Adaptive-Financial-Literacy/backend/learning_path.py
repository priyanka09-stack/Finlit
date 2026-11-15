from ml_model import build_features, predict_pass_probability, model_available
UNASSESSED = 50  # jis topic ka diagnostic score nahi hai, use neutral maano (0 nahi)

def target_level(percent):
    """Topic score se student ka level (rule-based fallback)."""
    if percent < 50:
        return "easy"
    if percent < 80:
        return "medium"
    return "hard"


def get_pace(topic_scores):
    """Average score se pace aur modules per session."""
    if not topic_scores:
        return "normal", 2
    avg = sum(s["percent"] for s in topic_scores.values()) / len(topic_scores)
    if avg < 40:
        return "slow", 1
    if avg < 70:
        return "normal", 2
    return "fast", 3


def zone_bonus(p):
    """Seekhne ka sahi zone: pass probability ~70% pe sabse zyada bonus (max 30), 40% se kam ya 100% pe zero."""
    return 30 * max(0.0, 1 - abs(p - 0.7) / 0.3)


def build_path(student, modules, attempt_count=0, past_pass_rate=0.5):
    topic_scores = student.get("topic_scores", {})
    risk = student.get("risk_profile")
    completed = student.get("completed_modules", [])

    path = []
    for m in modules:
        if m["id"] in completed:
            continue

        percent = topic_scores.get(m["topic"], {}).get("percent", UNASSESSED)
        risk_fit = risk in m["risk_tags"]

        priority = 100 - percent
        reasons = [f"your {m['topic']} score is {percent}%"]

        if risk_fit:
            priority += 20
            reasons.append(f"suits your {risk} profile")

        probability = None
        if model_available():
            features = build_features(student, m, attempt_count, past_pass_rate, len(modules))
            probability = predict_pass_probability(features)
            priority += zone_bonus(probability)
            reasons.append(f"predicted success {round(probability * 100)}%")
        elif m["difficulty"] == target_level(percent):
            priority += 15
            reasons.append(f"matches your {m['difficulty']} level")

        path.append({
            "id": m["id"],
            "title": m["title"],
            "topic": m["topic"],
            "difficulty": m["difficulty"],
            "priority": round(priority, 1),
            "pass_probability": round(probability * 100) if probability is not None else None,
            "reason": ", ".join(reasons),
        })

    path.sort(key=lambda x: (-x["priority"], x["id"]))
    return path
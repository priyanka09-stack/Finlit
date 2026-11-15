import os
from flask import Flask, jsonify , request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
from risk_questions import RISK_QUESTIONS, calculate_profile
load_dotenv()
from diagnostic_questions import DIAGNOSTIC_QUESTIONS, evaluate_diagnostic
from learning_path import build_path, get_pace
from module_quizzes import MODULE_QUIZZES, PASS_PERCENT, evaluate_module_quiz, update_mastery
from market import STOCKS, INDEX_SYMBOL, get_quote
from portfolio_analysis import analyze_portfolio
from concurrent.futures import ThreadPoolExecutor
from ml_model import build_features, predict_pass_probability, model_info
from auth import hash_password, verify_password, make_token, read_token

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]


def serialize(doc):
    """MongoDB ke ObjectId ko string mein badalta hai taaki JSON ban sake."""
    doc["_id"] = str(doc["_id"])
    doc.pop("password_hash", None)
    return doc

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/db-test")
def db_test():
    client.admin.command("ping")
    return jsonify({"db": "connected"})

from functools import wraps


def student_access(fn):
    """Sirf wahi student (ya educator) jiska ye data hai. Baaki ko 401/403."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"error": "please log in"}), 401
        if user.get("role") == "educator":
            return fn(*args, **kwargs)  # Stage 3 mein yahan "apni class" ka check jodenge
        if user.get("role") != "student" or user.get("id") != kwargs.get("student_id"):
            return jsonify({"error": "not allowed"}), 403
        return fn(*args, **kwargs)
    return wrapper 

@app.route("/api/students", methods=["POST"])
def create_student():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400
    if db.students.find_one({"email": email}):
        return jsonify({"error": "email already registered"}), 409

    student = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "risk_profile": None,
        "current_difficulty": "easy",
        "topic_scores": {},
        "created_at": datetime.utcnow().isoformat(),
    }
    result = db.students.insert_one(student)
    student["_id"] = str(result.inserted_id)
    student.pop("password_hash")
    return jsonify({"token": make_token(student["_id"], "student"), "student": student}), 201

def current_user():
    """Authorization: Bearer <token> se logged-in user nikalta hai."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return read_token(header[7:])


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    student = db.students.find_one({"email": email})
    if not student or not student.get("password_hash") or not verify_password(student["password_hash"], password):
        # email galat hai ya password, ye jaanbujhke nahi batate
        return jsonify({"error": "invalid email or password"}), 401

    token = make_token(str(student["_id"]), "student")
    return jsonify({"token": token, "student": serialize(student)})


@app.route("/api/me", methods=["GET"])
def me():
    user = current_user()
    if not user or user.get("role") != "student":
        return jsonify({"error": "please log in"}), 401
    student = find_student(user["id"])
    if not student:
        return jsonify({"error": "please log in"}), 401
    return jsonify(serialize(student))


@app.route("/api/students/<student_id>/password", methods=["POST"])
@student_access
def change_password(student_id):
    user = current_user()
    if not user or user.get("role") != "student" or user.get("id") != student_id:
        return jsonify({"error": "not allowed"}), 403

    data = request.get_json() or {}
    current = data.get("current_password") or ""
    new = data.get("new_password") or ""

    student = find_student(student_id)
    if not student or not student.get("password_hash") or not verify_password(student["password_hash"], current):
        return jsonify({"error": "current password is wrong"}), 400
    if len(new) < 6:
        return jsonify({"error": "new password must be at least 6 characters"}), 400

    db.students.update_one({"_id": student["_id"]}, {"$set": {"password_hash": hash_password(new)}})
    return jsonify({"message": "password updated"})


@app.route("/api/students", methods=["GET"])
def list_students():
    user = current_user()
    if not user or user.get("role") != "educator":
        return jsonify({"error": "not allowed"}), 403
    return jsonify([serialize(s) for s in db.students.find()])

@app.route("/api/students/<student_id>", methods=["GET"])
@student_access
def get_student(student_id):
    try:
        student = db.students.find_one({"_id": ObjectId(student_id)})
    except Exception:
        return jsonify({"error": "invalid student id"}), 400

    if not student:
        return jsonify({"error": "student not found"}), 404
    return jsonify(serialize(student))

@app.route("/api/risk-quiz", methods=["GET"])
def get_risk_quiz():
    # points student ko nahi dikhaate, sirf question aur option text
    questions = [
        {
            "id": q["id"],
            "question": q["question"],
            "options": [o["text"] for o in q["options"]],
        }
        for q in RISK_QUESTIONS
    ]
    return jsonify(questions)


@app.route("/api/students/<student_id>/risk-quiz", methods=["POST"])
@student_access
def submit_risk_quiz(student_id):
    data = request.get_json()
    answers = data.get("answers") if data else None

    if not isinstance(answers, list) or len(answers) != len(RISK_QUESTIONS):
        return jsonify({"error": "send answers for all questions"}), 400

    try:
        total, profile = calculate_profile(answers)
    except (IndexError, TypeError):
        return jsonify({"error": "invalid answer choice"}), 400

    try:
        result = db.students.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"risk_profile": profile, "risk_score": total}},
        )
    except Exception:
        return jsonify({"error": "invalid student id"}), 400

    if result.matched_count == 0:
        return jsonify({"error": "student not found"}), 404

    return jsonify({"risk_score": total, "risk_profile": profile})

@app.route("/api/modules", methods=["GET"])
def list_modules():
    modules = [serialize(m) for m in db.modules.find({}, {"content": 0, "quiz": 0}).sort("id", 1)]
    return jsonify(modules)


@app.route("/api/modules/<int:module_id>", methods=["GET"])
def get_module(module_id):
    module = db.modules.find_one({"id": module_id}, {"quiz": 0})
    if not module:
        return jsonify({"error": "module not found"}), 404
    return jsonify(serialize(module))
@app.route("/api/diagnostic", methods=["GET"])
def get_diagnostic():
    # answer student ko nahi dikhate
    questions = [
        {"id": q["id"], "topic": q["topic"], "question": q["question"], "options": q["options"]}
        for q in DIAGNOSTIC_QUESTIONS
    ]
    return jsonify(questions)


@app.route("/api/students/<student_id>/diagnostic", methods=["POST"])
@student_access
def submit_diagnostic(student_id):
    data = request.get_json()
    answers = data.get("answers") if data else None

    if not isinstance(answers, list) or len(answers) != len(DIAGNOSTIC_QUESTIONS):
        return jsonify({"error": "send answers for all questions"}), 400
    if not all(isinstance(a, int) and 0 <= a <= 2 for a in answers):
        return jsonify({"error": "each answer must be 0, 1 or 2"}), 400

    scores, weak_topics = evaluate_diagnostic(answers)

    try:
        result = db.students.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {
                "topic_scores": scores,
                "weak_topics": weak_topics,
                "diagnostic_done": True,
            }},
        )
    except Exception:
        return jsonify({"error": "invalid student id"}), 400

    if result.matched_count == 0:
        return jsonify({"error": "student not found"}), 404

    return jsonify({"topic_scores": scores, "weak_topics": weak_topics})

def attempt_stats(student_id):
    """Student ke pichle module-quiz attempts: kitne hue aur pass rate."""
    attempts = list(db.attempts.find(
        {"student_id": student_id, "passed": {"$exists": True}}, {"passed": 1}
    ))
    count = len(attempts)
    passed = sum(1 for a in attempts if a["passed"])
    return count, (passed / count if count else 0.5)


@app.route("/api/ml/info", methods=["GET"])
def ml_info():
    return jsonify(model_info() or {"error": "model not loaded"})



@app.route("/api/students/<student_id>/learning-path", methods=["GET"])
@student_access
def learning_path(student_id):
    try:
        student = db.students.find_one({"_id": ObjectId(student_id)})
    except Exception:
        return jsonify({"error": "invalid student id"}), 400
    if not student:
        return jsonify({"error": "student not found"}), 404

    if not student.get("diagnostic_done"):
        return jsonify({"error": "take the diagnostic quiz first"}), 400

    modules = list(db.modules.find({}, {"content": 0}))
    count, rate = attempt_stats(student_id)
    path = build_path(student, modules, count, rate)
    pace, per_session = get_pace(student.get("topic_scores", {}))

    return jsonify({
        "risk_profile": student.get("risk_profile"),
        "pace": pace,
        "modules_per_session": per_session,
        "path": path,
        "ml_model": model_info(),
    })


def get_quiz_questions(module_id):
    """Naye modules ka quiz module ke document mein hai, purane 6 ka module_quizzes.py mein."""
    module = db.modules.find_one({"id": module_id}, {"quiz": 1})
    if module and module.get("quiz"):
        return module["quiz"]
    return MODULE_QUIZZES.get(module_id)

@app.route("/api/modules/<int:module_id>/quiz", methods=["GET"])
def get_module_quiz(module_id):
    questions = get_quiz_questions(module_id)
    if not questions:
        return jsonify({"error": "quiz not found"}), 404
    # answer student ko nahi dikhate
    return jsonify([
        {"id": q["id"], "question": q["question"], "options": q["options"]}
        for q in questions
    ])


@app.route("/api/students/<student_id>/modules/<int:module_id>/quiz", methods=["POST"])
@student_access
def submit_module_quiz(student_id, module_id):
    data = request.get_json()
    answers = data.get("answers") if data else None

    questions = get_quiz_questions(module_id)
    if not questions:
        return jsonify({"error": "quiz not found"}), 404
    if not isinstance(answers, list) or len(answers) != len(questions):
        return jsonify({"error": "send answers for all questions"}), 400
    if not all(isinstance(a, int) and 0 <= a <= 2 for a in answers):
        return jsonify({"error": "each answer must be 0, 1 or 2"}), 400

    try:
        student = db.students.find_one({"_id": ObjectId(student_id)})
    except Exception:
        return jsonify({"error": "invalid student id"}), 400
    if not student:
        return jsonify({"error": "student not found"}), 404
    if not student.get("diagnostic_done"):
        return jsonify({"error": "take the diagnostic quiz first"}), 400

    module = db.modules.find_one({"id": module_id})
    topic = module["topic"]

    count, rate = attempt_stats(student_id)
    all_modules = list(db.modules.find({}, {"content": 0}))
    features = build_features(student, module, count, rate, len(all_modules))
    predicted = predict_pass_probability(features)

    quiz_percent = evaluate_module_quiz(questions, answers)
    passed = quiz_percent >= PASS_PERCENT

    old_percent = student.get("topic_scores", {}).get(topic, {}).get("percent", 0)
    new_percent = update_mastery(old_percent, quiz_percent)

    update = {"$set": {f"topic_scores.{topic}.percent": new_percent}}
    if passed:
        update["$addToSet"] = {"completed_modules": module_id}
    db.students.update_one({"_id": ObjectId(student_id)}, update)

    # attempt save (dashboard aur ML ke kaam aayega)
    db.attempts.insert_one({
        "student_id": student_id,
        "module_id": module_id,
        "topic": topic,
        "quiz_percent": quiz_percent,
        "passed": passed,
        "features": features,
        "predicted_pass_prob": predicted,
        "time": datetime.utcnow().isoformat(),
    })

    # updated student se naya path
    student = db.students.find_one({"_id": ObjectId(student_id)})
    modules = list(db.modules.find({}, {"content": 0}))
    count, rate = attempt_stats(student_id)
    path = build_path(student, modules, count, rate)
    pace, per_session = get_pace(student.get("topic_scores", {}))

    return jsonify({
        "quiz_percent": quiz_percent,
        "passed": passed,
        "message": "Module completed" if passed else "Not passed yet, re-read the module and try again",
        "topic": topic,
        "topic_percent_before": old_percent,
        "topic_percent_after": new_percent,
        "pace": pace,
        "next_module": path[0] if path else None,
                "predicted_pass_probability": round(predicted * 100) if predicted is not None else None,
    })


def safe_quote(symbol):
    try:
        return get_quote(symbol)
    except Exception:
        return None  # ek stock fail ho to baaki chalte rahein


@app.route("/api/market/stocks", methods=["GET"])
def market_stocks():
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(safe_quote, STOCKS.keys()))

    quotes = [q for q in results if q]
    if not quotes:
        return jsonify({"error": "market data unavailable right now"}), 502
    return jsonify(quotes)


@app.route("/api/market/<symbol>", methods=["GET"])
def market_symbol(symbol):
    if symbol not in STOCKS and symbol != INDEX_SYMBOL:
        return jsonify({"error": "symbol not supported"}), 404
    try:
        return jsonify(get_quote(symbol))
    except Exception:
        return jsonify({"error": "market data unavailable right now"}), 502


STARTING_CASH = 100000


def find_student(student_id):
    try:
        return db.students.find_one({"_id": ObjectId(student_id)})
    except Exception:
        return None


def get_portfolio(student_id):
    """Portfolio nahi hai to naya banata hai."""
    portfolio = db.portfolios.find_one({"student_id": student_id})
    if not portfolio:
        portfolio = {"student_id": student_id, "cash": STARTING_CASH, "holdings": []}
        db.portfolios.insert_one(portfolio)
    return portfolio


@app.route("/api/students/<student_id>/portfolio", methods=["GET"])
@student_access
def view_portfolio(student_id):
    if not find_student(student_id):
        return jsonify({"error": "student not found"}), 404

    portfolio = get_portfolio(student_id)

    holdings = []
    invested_value = 0
    for h in portfolio["holdings"]:
        try:
            current_price = get_quote(h["symbol"])["price"]
        except Exception:
            current_price = h["avg_price"]  # data na mile to buy price maan lo

        value = round(current_price * h["quantity"], 2)
        profit = round((current_price - h["avg_price"]) * h["quantity"], 2)
        invested_value += value
        holdings.append({
            "symbol": h["symbol"],
            "quantity": h["quantity"],
            "avg_price": h["avg_price"],
            "current_price": current_price,
            "value": value,
            "profit_loss": profit,
        })

    return jsonify({
        "cash": portfolio["cash"],
        "holdings": holdings,
        "invested_value": round(invested_value, 2),
        "total_value": round(portfolio["cash"] + invested_value, 2),
    })


@app.route("/api/students/<student_id>/trade", methods=["POST"])
@student_access
def trade(student_id):
    if not find_student(student_id):
        return jsonify({"error": "student not found"}), 404

    data = request.get_json() or {}
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    action = data.get("action")

    if symbol not in STOCKS:
        return jsonify({"error": "symbol not supported"}), 400
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "quantity must be a positive whole number"}), 400
    if action not in ("buy", "sell"):
        return jsonify({"error": "action must be buy or sell"}), 400

    try:
        price = get_quote(symbol)["price"]
    except Exception:
        return jsonify({"error": "market data unavailable right now"}), 502

    portfolio = get_portfolio(student_id)
    holdings = portfolio["holdings"]
    holding = next((h for h in holdings if h["symbol"] == symbol), None)
    amount = round(price * quantity, 2)

    if action == "buy":
        if amount > portfolio["cash"]:
            return jsonify({"error": "not enough cash"}), 400
        portfolio["cash"] = round(portfolio["cash"] - amount, 2)
        if holding:
            total_qty = holding["quantity"] + quantity
            holding["avg_price"] = round(
                (holding["avg_price"] * holding["quantity"] + amount) / total_qty, 2
            )
            holding["quantity"] = total_qty
        else:
            holdings.append({"symbol": symbol, "quantity": quantity, "avg_price": price})
    else:
        if not holding or holding["quantity"] < quantity:
            return jsonify({"error": "not enough shares to sell"}), 400
        portfolio["cash"] = round(portfolio["cash"] + amount, 2)
        holding["quantity"] -= quantity
        if holding["quantity"] == 0:
            holdings.remove(holding)

    db.portfolios.update_one(
        {"student_id": student_id},
        {"$set": {"cash": portfolio["cash"], "holdings": holdings}},
    )
    db.transactions.insert_one({
        "student_id": student_id,
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "price": price,
        "amount": amount,
        "time": datetime.utcnow().isoformat(),
    })

    return jsonify({
        "message": f"{action} successful",
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "amount": amount,
        "cash_left": portfolio["cash"],
    })


@app.route("/api/students/<student_id>/portfolio-feedback", methods=["GET"])
@student_access
def portfolio_feedback(student_id):
    student = find_student(student_id)
    if not student:
        return jsonify({"error": "student not found"}), 404

    portfolio = get_portfolio(student_id)

    holdings = []
    for h in portfolio["holdings"]:
        try:
            quote = get_quote(h["symbol"])
        except Exception:
            continue
        holdings.append({
            "symbol": h["symbol"],
            "sector": quote["sector"],
            "value": quote["price"] * h["quantity"],
            "volatility": quote["volatility"],
        })

    analysis = analyze_portfolio(holdings, student.get("risk_profile"))

    # feedback se related modules suggest karo (jo abhi complete nahi hue)
    completed = student.get("completed_modules", [])
    suggested = []
    for topic in analysis["focus_topics"]:
        m = db.modules.find_one(
            {"topic": topic, "id": {"$nin": completed}},
            {"content": 0},
            sort=[("id", 1)],
        )
        if m:
            suggested.append({"id": m["id"], "title": m["title"], "topic": topic})

    analysis["risk_profile"] = student.get("risk_profile")
    analysis["suggested_modules"] = suggested
    return jsonify(analysis)


@app.route("/api/market/condition", methods=["GET"])
def market_condition():
    try:
        index = get_quote(INDEX_SYMBOL)
    except Exception:
        return jsonify({"error": "market data unavailable right now"}), 502

    level = index["volatility_level"]
    change = index["change_percent"]

    # demo/testing ke liye: ?simulate=volatile
    if request.args.get("simulate") == "volatile":
        level = "high"
        change = -3.2

    volatile = level == "high" or abs(change) >= 1.5
    if volatile:
        condition = "volatile"
    elif level == "low":
        condition = "calm"
    else:
        condition = "normal"

    suggestion = None
    if volatile:
        m = db.modules.find_one(
            {"topic": "risk_return", "difficulty": "hard"}, {"content": 0}
        )
        if m:
            suggestion = {"id": m["id"], "title": m["title"]}

    return jsonify({
        "index": index["name"],
        "volatility_level": level,
        "change_percent": change,
        "condition": condition,
        "message": (
            "Markets are volatile right now. A good time to revise how volatility affects your portfolio."
            if volatile else "Markets look stable right now."
        ),
        "suggested_module": suggestion,
    })


if __name__ == "__main__":
    app.run(debug=True)

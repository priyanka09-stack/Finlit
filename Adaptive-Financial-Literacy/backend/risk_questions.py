RISK_QUESTIONS = [
    {
        "id": 1,
        "question": "Your investment falls 20% in one month. What do you do?",
        "options": [
            {"text": "Sell everything to avoid more loss", "points": 1},
            {"text": "Wait and do nothing", "points": 2},
            {"text": "Buy more at the lower price", "points": 3},
        ],
    },
    {
        "id": 2,
        "question": "How long can you keep your money invested?",
        "options": [
            {"text": "Less than 1 year", "points": 1},
            {"text": "1 to 5 years", "points": 2},
            {"text": "More than 5 years", "points": 3},
        ],
    },
    {
        "id": 3,
        "question": "Which outcome would you prefer?",
        "options": [
            {"text": "Guaranteed 5% return", "points": 1},
            {"text": "Likely 10% return, small chance of loss", "points": 2},
            {"text": "Possible 20% return, real chance of big loss", "points": 3},
        ],
    },
    {
        "id": 4,
        "question": "How much of your savings would you invest in stocks?",
        "options": [
            {"text": "Less than 10%", "points": 1},
            {"text": "10% to 40%", "points": 2},
            {"text": "More than 40%", "points": 3},
        ],
    },
    {
        "id": 5,
        "question": "How would you describe your knowledge of the stock market?",
        "options": [
            {"text": "Beginner", "points": 1},
            {"text": "Some basics", "points": 2},
            {"text": "Comfortable with it", "points": 3},
        ],
    },
]


def calculate_profile(answers):
    """answers = har question ke liye chosen option ka index (0, 1 ya 2)."""
    total = 0
    for q, choice in zip(RISK_QUESTIONS, answers):
        total += q["options"][choice]["points"]

    if total <= 8:
        profile = "Conservative"
    elif total <= 11:
        profile = "Moderate"
    else:
        profile = "Aggressive"

    return total, profile
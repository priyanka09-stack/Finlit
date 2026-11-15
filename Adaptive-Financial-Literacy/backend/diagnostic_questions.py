DIAGNOSTIC_QUESTIONS = [
    {"id": 1, "topic": "stock_basics",
     "question": "What is a stock?",
     "options": ["A loan given to a company", "A share of ownership in a company", "A government bond"],
     "answer": 1},
    {"id": 2, "topic": "stock_basics",
     "question": "What is a dividend?",
     "options": ["A fee paid to the broker", "A tax on stock gains", "A share of company profit paid to shareholders"],
     "answer": 2},
    {"id": 3, "topic": "risk_return",
     "question": "Higher potential return generally comes with:",
     "options": ["Lower risk", "No risk", "Higher risk"],
     "answer": 2},
    {"id": 4, "topic": "risk_return",
     "question": "Which is usually the lowest-risk option?",
     "options": ["Penny stock", "Fixed deposit", "Crypto"],
     "answer": 1},
    {"id": 5, "topic": "diversification",
     "question": "'Don't put all your eggs in one basket' means:",
     "options": ["Spread your investments across assets", "Invest in one stock only", "Keep only cash"],
     "answer": 0},
    {"id": 6, "topic": "diversification",
     "question": "What is a SIP?",
     "options": ["A type of loan", "Investing a fixed amount at regular intervals", "A one-time lump sum"],
     "answer": 1},
         {"id": 7, "topic": "mutual_funds",
     "question": "What is a mutual fund?",
     "options": ["A loan from a bank", "A pool of money from many investors, managed by a professional", "A single company's share"],
     "answer": 1},
    {"id": 8, "topic": "mutual_funds",
     "question": "What does the NAV of a fund tell you?",
     "options": ["The price of one unit of the fund", "The fund manager's salary", "The total number of investors"],
     "answer": 0},
    {"id": 9, "topic": "market_analysis",
     "question": "Which approach studies a company's revenue and profit to judge its value?",
     "options": ["Fundamental analysis", "Candlestick charts", "Trading volume"],
     "answer": 0},
    {"id": 10, "topic": "market_analysis",
     "question": "A candlestick on a price chart shows:",
     "options": ["Only the closing price", "Open, high, low and close for a period", "The company's dividend"],
     "answer": 1},
]


def evaluate_diagnostic(answers):
    """answers = har question ke liye chosen option ka index. Topic-wise score aur weak topics wapas deta hai."""
    scores = {}
    for q, choice in zip(DIAGNOSTIC_QUESTIONS, answers):
        topic = q["topic"]
        scores.setdefault(topic, {"correct": 0, "total": 0})
        scores[topic]["total"] += 1
        if choice == q["answer"]:
            scores[topic]["correct"] += 1

    for topic, s in scores.items():
        s["percent"] = round(100 * s["correct"] / s["total"])

    weak_topics = [t for t, s in scores.items() if s["percent"] < 60]
    return scores, weak_topics
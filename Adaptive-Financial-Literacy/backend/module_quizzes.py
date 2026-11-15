PASS_PERCENT = 60

MODULE_QUIZZES = {
    1: [
        {"id": 1, "question": "Buying a stock makes you:",
         "options": ["A lender to the company", "A part-owner of the company", "An employee of the company"], "answer": 1},
        {"id": 2, "question": "Where are stocks traded in India?",
         "options": ["NSE and BSE", "RBI", "Post offices"], "answer": 0},
    ],
    2: [
        {"id": 1, "question": "Sensex and Nifty are:",
         "options": ["Types of mutual funds", "Indices tracking large listed companies", "Government bonds"], "answer": 1},
        {"id": 2, "question": "P/E ratio is:",
         "options": ["Profit / expenses", "Dividend / share price", "Share price / earnings per share"], "answer": 2},
    ],
    3: [
        {"id": 1, "question": "Which usually has lower risk?",
         "options": ["Fixed deposit", "Stock", "Both are the same"], "answer": 0},
        {"id": 2, "question": "Risk tolerance means:",
         "options": ["How much profit you want", "How much loss you can stay calm about", "How many stocks you own"], "answer": 1},
    ],
    4: [
        {"id": 1, "question": "High volatility means:",
         "options": ["Price fluctuates sharply", "Price stays constant", "Company is profitable"], "answer": 0},
        {"id": 2, "question": "If returns are lower than inflation, your money:",
         "options": ["Grows in real value", "Stays the same in real value", "Loses real value"], "answer": 2},
    ],
    5: [
        {"id": 1, "question": "Diversification means:",
         "options": ["Putting all money in the best stock", "Spreading money across different investments", "Keeping money in cash only"], "answer": 1},
        {"id": 2, "question": "Which is more diversified?",
         "options": ["5 stocks from different sectors", "5 stocks from the same sector", "1 stock"], "answer": 0},
    ],
    6: [
        {"id": 1, "question": "In a SIP you invest:",
         "options": ["Only when prices are low", "Only once in a lifetime", "A fixed amount at regular intervals"], "answer": 2},
        {"id": 2, "question": "Rupee cost averaging means you:",
         "options": ["Buy fewer units when prices are low", "Buy more units when prices are low", "Always pay the same price"], "answer": 1},
    ],
}


def evaluate_module_quiz(questions, answers):
    #percent score of quiz attempt
    correct = sum(1 for q, a in zip(questions, answers) if a == q["answer"])
    return round(100 * correct / len(questions))


def update_mastery(old_percent, quiz_percent):
    """Purane topic score aur naye quiz score ka average."""
    return round(0.5 * old_percent + 0.5 * quiz_percent)
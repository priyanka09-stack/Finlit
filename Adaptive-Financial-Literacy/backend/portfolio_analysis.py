# Ye thresholds tune kar sakte ho (daily volatility % ke hisaab se)
RISK_LOW = 1.0
RISK_HIGH = 1.5
CONCENTRATION_LIMIT = 50  # ek stock itne % se zyada ho to warning

ORDER = ["Conservative", "Moderate", "Aggressive"]


def analyze_portfolio(holdings, risk_profile):
    """holdings = [{symbol, sector, value, volatility}]"""
    total = sum(h["value"] for h in holdings)
    if total == 0:
        return {
            "portfolio_risk": None,
            "avg_volatility": None,
            "top_holding_percent": None,
            "sector_count": 0,
            "feedback": ["You have not invested yet. Buy a few stocks to get feedback."],
            "focus_topics": [],
        }

    # value-weighted average volatility
    avg_vol = round(sum(h["volatility"] * h["value"] for h in holdings) / total, 2)
    if avg_vol < RISK_LOW:
        level = "Conservative"
    elif avg_vol < RISK_HIGH:
        level = "Moderate"
    else:
        level = "Aggressive"

    top = max(holdings, key=lambda h: h["value"])
    top_percent = round(100 * top["value"] / total)
    sectors = {h["sector"] for h in holdings}

    feedback = []
    topics = []

    # 1) portfolio risk vs risk profile
    if risk_profile in ORDER:
        gap = ORDER.index(level) - ORDER.index(risk_profile)
        if gap > 0:
            feedback.append(
                f"Your portfolio behaves like a {level} one, but your risk profile is {risk_profile}. "
                "It is riskier than what you said you are comfortable with."
            )
            topics.append("risk_return")
        elif gap < 0:
            feedback.append(
                f"Your portfolio is safer than your {risk_profile} profile. "
                "That is fine, but you may be leaving potential returns on the table."
            )
        else:
            feedback.append(f"Your portfolio matches your {risk_profile} risk profile. Good alignment.")
    else:
        feedback.append("Take the risk quiz to compare your portfolio with your risk profile.")

    # 2) concentration
    if top_percent > CONCENTRATION_LIMIT:
        feedback.append(
            f"{top['symbol'].replace('.NS', '')} is {top_percent}% of your invested money. "
            "Too much in one stock increases risk."
        )
        topics.append("diversification")

    # 3) sector spread
    if len(sectors) == 1:
        feedback.append("All your stocks are from one sector. Try adding stocks from other sectors.")
        if "diversification" not in topics:
            topics.append("diversification")

    return {
        "portfolio_risk": level,
        "avg_volatility": avg_vol,
        "top_holding_percent": top_percent,
        "sector_count": len(sectors),
        "feedback": feedback,
        "focus_topics": topics,
    }
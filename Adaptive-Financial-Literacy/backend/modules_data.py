MODULES = [
    {
        "id": 1, "topic": "stock_basics", "difficulty": "easy",
        "title": "What is a Stock?",
        "risk_tags": ["Conservative", "Moderate", "Aggressive"],
        "content": [
            "A stock is a share of ownership in a company. When you buy a stock, you become a part-owner of that company.",
            "Stocks are bought and sold on exchanges like NSE and BSE. Prices move based on demand, supply and company performance.",
            "Companies may share part of their profit with shareholders as dividends.",
        ],
    },
    {
        "id": 2, "topic": "stock_basics", "difficulty": "medium",
        "title": "Reading the Market: Sensex, Nifty and P/E",
        "risk_tags": ["Moderate", "Aggressive"],
        "content": [
            "Sensex and Nifty are indices that track a group of large listed companies. A rising index suggests the broader market is going up.",
            "Market capitalisation is the total value of a company's shares: share price multiplied by number of shares.",
            "The P/E ratio is share price divided by earnings per share. A high P/E can mean high expectations or an expensive stock.",
        ],
    },
    {
        "id": 3, "topic": "risk_return", "difficulty": "easy",
        "title": "Risk and Return",
        "risk_tags": ["Conservative", "Moderate", "Aggressive"],
        "content": [
            "Risk is the chance that an investment loses value. Return is the profit you earn. Higher potential return usually comes with higher risk.",
            "Fixed deposits are low risk with stable returns. Stocks can give higher returns but their prices go up and down.",
            "Know your own risk tolerance before investing: how much loss can you stay calm about?",
        ],
    },
    {
        "id": 4, "topic": "risk_return", "difficulty": "hard",
        "title": "Volatility and Inflation Risk",
        "risk_tags": ["Moderate", "Aggressive"],
        "content": [
            "Volatility measures how much a price fluctuates. A highly volatile stock can rise or fall sharply in a short time.",
            "Inflation reduces the purchasing power of money. If your returns are lower than inflation, your money loses real value.",
            "A longer investment horizon smooths short-term fluctuations, but it never guarantees profit.",
        ],
    },
    {
        "id": 5, "topic": "diversification", "difficulty": "easy",
        "title": "Do Not Put All Eggs in One Basket",
        "risk_tags": ["Conservative", "Moderate", "Aggressive"],
        "content": [
            "Diversification means spreading your money across different investments so one bad performer does not hurt you much.",
            "A mutual fund pools money from many investors and invests it in many assets, giving instant diversification.",
            "Five stocks from five different sectors are safer than five stocks from the same sector.",
        ],
    },
    {
        "id": 6, "topic": "diversification", "difficulty": "medium",
        "title": "SIP and Rupee Cost Averaging",
        "risk_tags": ["Conservative", "Moderate"],
        "content": [
            "A SIP (Systematic Investment Plan) invests a fixed amount at regular intervals, for example Rs 1000 every month.",
            "Rupee cost averaging means you buy more units when prices are low and fewer when prices are high, which lowers your average cost.",
            "Diversification reduces company and sector risk, but it cannot remove market-wide risk.",
        ],
    },
        {
        "id": 7, "topic": "mutual_funds", "difficulty": "easy",
        "title": "Mutual Funds Explained",
        "risk_tags": ["Conservative", "Moderate", "Aggressive"],
        "content": [
            "A mutual fund collects money from many investors and invests it in a mix of stocks, bonds or other assets. A professional fund manager decides where the money goes.",
            "When you invest, you buy units of the fund. The price of one unit is called the NAV (Net Asset Value), and it changes every day with the value of the fund's investments.",
            "Because your money is spread across many companies, a mutual fund gives you instant diversification. Funds charge a small yearly fee called the expense ratio, which reduces your returns, so it is worth comparing.",
        ],
        "quiz": [
            {"id": 1, "question": "In a mutual fund, who decides where the pooled money is invested?",
             "options": ["Each investor separately", "A professional fund manager", "The stock exchange"], "answer": 1},
            {"id": 2, "question": "What does NAV stand for?",
             "options": ["Net Asset Value", "New Annual Variation", "National Average Value"], "answer": 0},
        ],
    },
    {
        "id": 8, "topic": "mutual_funds", "difficulty": "medium",
        "title": "Types of Mutual Funds",
        "risk_tags": ["Conservative", "Moderate"],
        "content": [
            "Equity funds invest mainly in stocks. They can give higher returns over long periods, but their value can fall sharply in the short term.",
            "Debt funds invest in bonds and other fixed-income instruments. They are usually more stable than equity funds, with lower expected returns.",
            "Index funds simply copy an index such as Nifty 50 instead of trying to beat it, and they usually have lower fees. Hybrid funds mix equity and debt in a single fund.",
        ],
        "quiz": [
            {"id": 1, "question": "Which type of fund simply copies an index like Nifty 50?",
             "options": ["Index fund", "Debt fund", "Hybrid fund"], "answer": 0},
            {"id": 2, "question": "Which fund type is usually more stable but offers lower expected returns?",
             "options": ["Equity fund", "Debt fund", "Sectoral equity fund"], "answer": 1},
        ],
    },
    {
        "id": 9, "topic": "market_analysis", "difficulty": "easy",
        "title": "Reading Stock Charts and Trends",
        "risk_tags": ["Conservative", "Moderate", "Aggressive"],
        "content": [
            "A stock chart shows how a price has moved over time. A line chart connects closing prices, while a candlestick shows the open, high, low and close for each period.",
            "A trend is the general direction of the price: up (an uptrend), down (a downtrend) or sideways. Many investors look at the trend before deciding when to buy or sell.",
            "Volume is the number of shares traded. A price move on high volume is usually considered more meaningful than one on low volume.",
        ],
        "quiz": [
            {"id": 1, "question": "What does 'volume' mean on a stock chart?",
             "options": ["The price of one share", "The number of shares traded", "The company's yearly profit"], "answer": 1},
            {"id": 2, "question": "A price that keeps moving upward over time is called:",
             "options": ["A downtrend", "A sideways market", "An uptrend"], "answer": 2},
        ],
    },
    {
        "id": 10, "topic": "market_analysis", "difficulty": "hard",
        "title": "Fundamental vs Technical Analysis",
        "risk_tags": ["Moderate", "Aggressive"],
        "content": [
            "Fundamental analysis studies a company's business, such as its revenue, profit, debt and growth, to estimate what the stock is really worth. It is mostly used for long-term investing.",
            "Technical analysis studies price charts and trading volume to understand market behaviour and timing. It is more common for short-term trading.",
            "Ratios like P/E, debt-to-equity and return on equity are tools of fundamental analysis. No method can predict the market with certainty, so many investors use both approaches and still diversify.",
        ],
        "quiz": [
            {"id": 1, "question": "Which analysis looks at a company's revenue, profit and debt?",
             "options": ["Fundamental analysis", "Technical analysis", "Chart pattern analysis"], "answer": 0},
            {"id": 2, "question": "Technical analysis mainly studies:",
             "options": ["A company's balance sheet", "Price charts and trading volume", "Government policy documents"], "answer": 1},
        ],
    },
]
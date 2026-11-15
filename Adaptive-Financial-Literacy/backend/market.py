import time
import yfinance as yf

STOCKS = {
    "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Energy"},
    "TCS.NS": {"name": "Tata Consultancy Services", "sector": "IT"},
    "INFY.NS": {"name": "Infosys", "sector": "IT"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Banking"},
    "ITC.NS": {"name": "ITC", "sector": "FMCG"},
    "SUNPHARMA.NS": {"name": "Sun Pharma", "sector": "Pharma"},
        "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Banking"},
    "SBIN.NS": {"name": "State Bank of India", "sector": "Banking"},
    "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "sector": "Banking"},
    "AXISBANK.NS": {"name": "Axis Bank", "sector": "Banking"},
    "WIPRO.NS": {"name": "Wipro", "sector": "IT"},
    "HCLTECH.NS": {"name": "HCL Technologies", "sector": "IT"},
    "ONGC.NS": {"name": "ONGC", "sector": "Energy"},
    "NTPC.NS": {"name": "NTPC", "sector": "Energy"},
    "HINDUNILVR.NS": {"name": "Hindustan Unilever", "sector": "FMCG"},
    "NESTLEIND.NS": {"name": "Nestle India", "sector": "FMCG"},
    "DRREDDY.NS": {"name": "Dr. Reddy's Laboratories", "sector": "Pharma"},
    "CIPLA.NS": {"name": "Cipla", "sector": "Pharma"},
    "MARUTI.NS": {"name": "Maruti Suzuki", "sector": "Auto"},
    "EICHERMOT.NS": {"name": "Eicher Motors", "sector": "Auto"},
    "TATASTEEL.NS": {"name": "Tata Steel", "sector": "Metals"},
    "JSWSTEEL.NS": {"name": "JSW Steel", "sector": "Metals"},
    "BHARTIARTL.NS": {"name": "Bharti Airtel", "sector": "Telecom"},
    "BAJFINANCE.NS": {"name": "Bajaj Finance", "sector": "Finance"},
    "LT.NS": {"name": "Larsen & Toubro", "sector": "Infrastructure"},
    "ULTRACEMCO.NS": {"name": "UltraTech Cement", "sector": "Infrastructure"},
}

INDEX_SYMBOL = "^NSEI"
INDEX_INFO = {"name": "Nifty 50", "sector": "Index"}

CACHE_SECONDS = 300  # 5 minute cache, taaki baar baar API call na ho
_cache = {}


def volatility_label(vol):
    """Daily price swing (%) se label."""
    if vol < 1:
        return "low"
    if vol < 1.8:
        return "medium"
    return "high"


def get_quote(symbol):
    now = time.time()
    cached = _cache.get(symbol)
    if cached and now - cached["time"] < CACHE_SECONDS:
        return cached["data"]

    history = yf.Ticker(symbol).history(period="1mo")
    if history.empty:
        raise ValueError(f"no data for {symbol}")

    closes = history["Close"].dropna()
    if closes.empty:
        raise ValueError(f"no data for {symbol}")
    price = round(float(closes.iloc[-1]), 2)
    previous = float(closes.iloc[-2]) if len(closes) > 1 else price
    change_percent = round((price - previous) / previous * 100, 2)

    daily_returns = closes.pct_change().dropna()
    std = daily_returns.std()
    volatility = round(float(std) * 100, 2) if std == std else 0.0

    info = STOCKS.get(symbol, INDEX_INFO)
    data = {
        "symbol": symbol,
        "name": info["name"],
        "sector": info["sector"],
        "price": price,
        "change_percent": change_percent,
        "volatility": volatility,
        "volatility_level": volatility_label(volatility),
    }
    _cache[symbol] = {"time": now, "data": data}
    return data
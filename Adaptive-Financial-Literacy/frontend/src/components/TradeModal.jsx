import { useState } from "react";
import { X, Minus, Plus } from "lucide-react";
import { api } from "../api";
import { useStudent } from "../StudentContext";
import { formatINR } from "../utils";

export default function TradeModal({ stock, portfolio, onClose, onDone }) {
  const { student } = useStudent();
  const [action, setAction] = useState("buy");
  const [quantity, setQuantity] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const symbol = stock.symbol.replace(".NS", "");
  const owned = portfolio?.holdings.find((h) => h.symbol === stock.symbol)?.quantity || 0;
  const cash = portfolio?.cash ?? 0;
  const amount = stock.price * quantity;
  const maxBuy = Math.floor(cash / stock.price);
  const tooMuch = action === "buy" ? amount > cash : quantity > owned;

  function clear() {
    setError("");
    setSuccess("");
  }

  function setQty(value) {
    const n = Math.max(1, Math.floor(Number(value) || 1));
    setQuantity(n);
    clear();
  }

  function switchAction(a) {
    setAction(a);
    clear();
  }

  async function submit() {
    setBusy(true);
    clear();
    try {
      const res = await api.trade(student._id, stock.symbol, quantity, action);
      setSuccess(`${action === "buy" ? "Bought" : "Sold"} ${quantity} x ${symbol} at ${formatINR(res.price)}`);
      await onDone();
      setQuantity(1);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="card modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <h2>{symbol}</h2>
            <span className="stock-name">
              {stock.name} · {formatINR(stock.price)}
            </span>
          </div>
          <button className="icon-btn" onClick={onClose} title="Close">
            <X size={20} />
          </button>
        </div>

        <div className="seg">
          <button className={action === "buy" ? "active-buy" : ""} onClick={() => switchAction("buy")}>
            Buy
          </button>
          <button className={action === "sell" ? "active-sell" : ""} onClick={() => switchAction("sell")}>
            Sell
          </button>
        </div>

        <div className="field" style={{ marginTop: 18 }}>
          <label>Quantity</label>
          <div className="qty">
            <button className="btn btn-ghost qty-btn" style={{ width: "auto" }} onClick={() => setQty(quantity - 1)}>
              <Minus size={18} />
            </button>
            <input type="number" min="1" value={quantity} onChange={(e) => setQty(e.target.value)} />
            <button className="btn btn-ghost qty-btn" style={{ width: "auto" }} onClick={() => setQty(quantity + 1)}>
              <Plus size={18} />
            </button>
          </div>
        </div>

        <div className="sum">
          <div className="sum-row">
            <span>{action === "buy" ? "Estimated cost" : "Estimated proceeds"}</span>
            <strong>{formatINR(amount)}</strong>
          </div>
          <div className="sum-row">
            <span>Cash available</span>
            <span>{formatINR(cash)}</span>
          </div>
          <div className="sum-row">
            <span>Shares you own</span>
            <span>{owned}</span>
          </div>
        </div>

        {action === "buy" && tooMuch && (
          <div className="error-text">Not enough cash. You can buy up to {maxBuy} share(s).</div>
        )}
        {action === "sell" && tooMuch && (
          <div className="error-text">You only own {owned} share(s) of {symbol}.</div>
        )}
        {error && <div className="error-text">{error}</div>}
        {success && <div className="success-text">{success}</div>}

        <button
          className={"btn " + (action === "buy" ? "btn-primary" : "btn-sell")}
          disabled={busy || tooMuch}
          onClick={submit}
        >
          {busy ? "Placing order..." : `${action === "buy" ? "Buy" : "Sell"} ${quantity} share${quantity > 1 ? "s" : ""}`}
        </button>
      </div>
    </div>
  );
}
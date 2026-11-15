import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { Lightbulb, CheckCircle2, AlertTriangle, Info, ArrowRight, ShoppingCart } from "lucide-react";
import { api } from "../api";
import { useStudent } from "../StudentContext";
import { formatINR } from "../utils";

const STARTING_CASH = 100000;
const COLORS = ["#10b981", "#06b6d4", "#8b5cf6", "#f59e0b", "#ec4899", "#3b82f6", "#84cc16", "#f97316"];
const CASH_COLOR = "#475569";
const sign = (n) => (n >= 0 ? "+" : "");

function tone(text) {
  if (text.includes("Good alignment")) return "ok";
  if (text.includes("safer than") || text.includes("not invested") || text.includes("Take the risk quiz")) return "info";
  return "warn";
}
const FB_ICON = { ok: CheckCircle2, warn: AlertTriangle, info: Info };

export default function Portfolio() {
  const { student } = useStudent();
  const [portfolio, setPortfolio] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getPortfolio(student._id), api.getPortfolioFeedback(student._id)])
      .then(([p, f]) => {
        setPortfolio(p);
        setFeedback(f);
      })
      .catch((e) => setError(e.message));
  }, [student._id, student.risk_profile]);

  if (error) return <div className="error-text">{error}</div>;
  if (!portfolio) return <div className="card coming">Loading your portfolio...</div>;

  const holdings = portfolio.holdings;
  const totalPL = holdings.reduce((s, h) => s + h.profit_loss, 0);
  const costBasis = holdings.reduce((s, h) => s + h.avg_price * h.quantity, 0);
  const plPct = costBasis ? (totalPL / costBasis) * 100 : 0;
  const returnPct = ((portfolio.total_value - STARTING_CASH) / STARTING_CASH) * 100;

  const chartData = [
    { name: "Cash", value: portfolio.cash, color: CASH_COLOR },
    ...holdings.map((h, i) => ({
      name: h.symbol.replace(".NS", ""),
      value: h.value,
      color: COLORS[i % COLORS.length],
    })),
  ];

  return (
    <>
      <div className="page-head">
        <h1>Portfolio</h1>
        <p>Your virtual investments, how they are doing, and what to improve.</p>
      </div>

      <div className="grid-4">
        <div className="card stat compact">
          <div className="stat-label">Total value</div>
          <div className="stat-value">{formatINR(portfolio.total_value, 0)}</div>
          <div className={"stat-sub " + (returnPct >= 0 ? "up" : "down")}>
            {sign(returnPct)}{returnPct.toFixed(2)}% since start
          </div>
        </div>
        <div className="card stat compact">
          <div className="stat-label">Cash available</div>
          <div className="stat-value">{formatINR(portfolio.cash, 0)}</div>
          <div className="stat-sub">
            {((portfolio.cash / portfolio.total_value) * 100).toFixed(0)}% of portfolio
          </div>
        </div>
        <div className="card stat compact">
          <div className="stat-label">Invested</div>
          <div className="stat-value">{formatINR(portfolio.invested_value, 0)}</div>
          <div className="stat-sub">{holdings.length} stock{holdings.length === 1 ? "" : "s"}</div>
        </div>
        <div className="card stat compact">
          <div className="stat-label">Profit / Loss</div>
          <div className="stat-value">{sign(totalPL)}{formatINR(totalPL)}</div>
          <div className={"stat-sub " + (totalPL >= 0 ? "up" : "down")}>
            {sign(plPct)}{plPct.toFixed(2)}% on invested
          </div>
        </div>
      </div>

      {holdings.length === 0 ? (
        <div className="card coming">
          <p style={{ marginBottom: 18 }}>
            Your portfolio is empty. Buy a few stocks with your virtual cash to get started and to receive feedback.
          </p>
          <Link to="/market" className="btn btn-primary">
            <ShoppingCart size={18} /> Browse market
          </Link>
        </div>
      ) : (
        <>
          <div className="two-col">
            <div className="card">
              <div className="card-title">Allocation</div>
              <div className="donut-wrap">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={68}
                      outerRadius={100}
                      paddingAngle={2}
                      stroke="none"
                    >
                      {chartData.map((d) => (
                        <Cell key={d.name} fill={d.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(v) => formatINR(v)}
                      contentStyle={{
                        background: "#16213a",
                        border: "1px solid rgba(148,163,184,0.2)",
                        borderRadius: 10,
                      }}
                      itemStyle={{ color: "#e8edf7" }}
                      labelStyle={{ color: "#e8edf7" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="donut-center">
                  <div>
                    <small>Total</small>
                    <strong>{formatINR(portfolio.total_value, 0)}</strong>
                  </div>
                </div>
              </div>

              <div className="legend">
                {chartData.map((d) => (
                  <div className="legend-row" key={d.name}>
                    <span className="legend-dot" style={{ background: d.color }} />
                    <span>{d.name}</span>
                    <span>{((d.value / portfolio.total_value) * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-title"><Lightbulb size={20} /> Portfolio feedback</div>

              <div className="badge-row">
                <span className="badge">Portfolio style: {feedback.portfolio_risk}</span>
                <span className="badge amber">Your profile: {feedback.risk_profile || "not set"}</span>
              </div>

              <div className="metric-row">
                <div className="metric">
                  <small>Avg volatility</small>
                  <strong>{feedback.avg_volatility}%</strong>
                </div>
                <div className="metric">
                  <small>Top holding</small>
                  <strong>{feedback.top_holding_percent}%</strong>
                </div>
                <div className="metric">
                  <small>Sectors</small>
                  <strong>{feedback.sector_count}</strong>
                </div>
              </div>

              <ul className="feedback-list">
                {feedback.feedback.map((text, i) => {
                  const t = tone(text);
                  const Icon = FB_ICON[t];
                  return (
                    <li key={i} className={"feedback-item fb-" + t}>
                      <Icon size={18} />
                      <span>{text}</span>
                    </li>
                  );
                })}
              </ul>

              {feedback.suggested_modules.length > 0 && (
                <>
                  <div className="eyebrow" style={{ marginBottom: 10 }}>Recommended for you</div>
                  <div className="rec-list">
                    {feedback.suggested_modules.map((m) => (
                      <Link key={m.id} to={`/learn/${m.id}`} className="btn btn-ghost">
                        {m.title} <ArrowRight size={16} />
                      </Link>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-title">Holdings</div>
            <div className="table-wrap">
              <table className="holdings">
                <thead>
                  <tr>
                    <th>Stock</th>
                    <th>Qty</th>
                    <th>Avg price</th>
                    <th>Current</th>
                    <th>Value</th>
                    <th>P / L</th>
                  </tr>
                </thead>
                <tbody>
                  {holdings.map((h) => {
                    const pct = (h.profit_loss / (h.avg_price * h.quantity)) * 100;
                    return (
                      <tr key={h.symbol}>
                        <td className="sym">{h.symbol.replace(".NS", "")}</td>
                        <td>{h.quantity}</td>
                        <td>{formatINR(h.avg_price)}</td>
                        <td>{formatINR(h.current_price)}</td>
                        <td>{formatINR(h.value)}</td>
                        <td className={h.profit_loss >= 0 ? "pl-up" : "pl-down"}>
                          {sign(h.profit_loss)}{formatINR(h.profit_loss)}
                          <span className="pl-sub">{sign(pct)}{pct.toFixed(2)}%</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div style={{ marginTop: 18 }}>
              <Link to="/market" className="btn btn-ghost btn-sm">
                <ShoppingCart size={16} /> Trade more
              </Link>
            </div>
          </div>
        </>
      )}
    </>
  );
}
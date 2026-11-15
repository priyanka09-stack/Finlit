import { useEffect, useState, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import {
  TrendingUp, TrendingDown, Activity, ArrowRight, Search, X, ChevronLeft, ChevronRight,
} from "lucide-react";
import { api } from "../api";
import { useStudent } from "../StudentContext";
import { formatINR } from "../utils";
import TradeModal from "../components/TradeModal";

const VOL_BADGE = { low: "green", medium: "amber", high: "red" };
const CONDITION_BADGE = { calm: "green", normal: "amber", volatile: "red" };
const PAGE_SIZE = 6;

export default function Market() {
  const { student } = useStudent();
  const [stocks, setStocks] = useState(null);
  const [condition, setCondition] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [simulate, setSimulate] = useState(false);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [sector, setSector] = useState("All");
  const [page, setPage] = useState(1);
  const topRef = useRef(null);

  const loadPortfolio = useCallback(
    () => api.getPortfolio(student._id).then(setPortfolio).catch((e) => setError(e.message)),
    [student._id]
  );


    useEffect(() => {
    api
      .getStocks()
      .then((data) => {
        if (Array.isArray(data)) setStocks(data);
        else setError(data?.error || "Market API sent an unexpected response");
      })
      .catch((e) => setError(e.message));
    loadPortfolio();
  }, [loadPortfolio]);

  useEffect(() => {
    api.getMarketCondition(simulate).then(setCondition).catch(() => setCondition(null));
  }, [simulate]);

  const sectors = stocks ? ["All", ...new Set(stocks.map((s) => s.sector))] : ["All"];
  const filtered = (stocks || []).filter(
    (s) =>
      (sector === "All" || s.sector === sector) &&
      (s.symbol + " " + s.name).toLowerCase().includes(query.trim().toLowerCase())
  );

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const start = (page - 1) * PAGE_SIZE;
  const shown = filtered.slice(start, start + PAGE_SIZE);

  function goTo(p) {
    setPage(p);
    topRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <>
      <div className="page-head">
        <h1>Market</h1>
        <p>
          Practise with real prices and virtual money.
          {portfolio && <> Cash available: <strong>{formatINR(portfolio.cash)}</strong></>}
        </p>
      </div>

      {error && <div className="error-text">{error}</div>}

      {condition && (
        <div className={"card market-banner " + condition.condition}>
          <div className="stat-icon"><Activity size={24} /></div>
          <div className="banner-main">
            <div className="badge-row" style={{ marginBottom: 6 }}>
              <span className="eyebrow">{condition.index} today</span>
              <span className={"badge " + CONDITION_BADGE[condition.condition]}>{condition.condition}</span>
            </div>
            <p className="banner-text">{condition.message}</p>
          </div>
          <div className="banner-actions">
            {condition.suggested_module && (
              <Link to={`/learn/${condition.suggested_module.id}`} className="btn btn-ghost btn-sm">
                Revise: {condition.suggested_module.title} <ArrowRight size={16} />
              </Link>
            )}
            <button className="btn btn-ghost btn-sm" onClick={() => setSimulate(!simulate)}>
              {simulate ? "Back to live market" : "Preview volatile market"}
            </button>
          </div>
        </div>
      )}

      {stocks && (
        <div className="toolbar" ref={topRef}>
          <div className="search">
            <Search size={18} />
            <input
              placeholder="Search stocks, e.g. bank or TCS"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setPage(1);
              }}
            />
            {query && (
              <button
                className="clear-btn"
                title="Clear search"
                onClick={() => {
                  setQuery("");
                  setPage(1);
                }}
              >
                <X size={16} />
              </button>
            )}
          </div>
          <div className="chips">
            {sectors.map((sec) => (
              <button
                key={sec}
                className={"chip" + (sector === sec ? " active" : "")}
                onClick={() => {
                  setSector(sec);
                  setPage(1);
                }}
              >
                {sec}
              </button>
            ))}
          </div>
          <div className="result-count">
            {filtered.length === 0
              ? "No stocks found"
              : `Showing ${start + 1}-${start + shown.length} of ${filtered.length} stocks`}
          </div>
        </div>
      )}

      <div className="stock-grid">
        {!stocks &&
          !error &&
          Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton" />)}

        {stocks &&
          shown.map((s) => {
            const up = s.change_percent >= 0;
            const owned = portfolio?.holdings.find((h) => h.symbol === s.symbol);
            return (
              <div className="card stock-card" key={s.symbol}>
                <div className="stock-top">
                  <div>
                    <div className="stock-symbol">{s.symbol.replace(".NS", "")}</div>
                    <div className="stock-name">{s.name}</div>
                  </div>
                  <span className="badge">{s.sector}</span>
                </div>

                <div className="price">{formatINR(s.price)}</div>
                <div className={"change " + (up ? "up" : "down")}>
                  {up ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                  {up ? "+" : ""}
                  {s.change_percent}% today
                </div>

                <div className="stock-foot">
                  <span className={"badge " + VOL_BADGE[s.volatility_level]}>
                    {s.volatility_level} volatility
                  </span>
                  <button className="btn btn-primary btn-sm" onClick={() => setSelected(s)}>
                    Trade
                  </button>
                </div>

                {owned && (
                  <div className="owned">
                    You own {owned.quantity} share{owned.quantity > 1 ? "s" : ""}
                  </div>
                )}
              </div>
            );
          })}
      </div>

      {stocks && filtered.length === 0 && (
        <div className="card coming">No stocks match your search.</div>
      )}

      {stocks && totalPages > 1 && (
        <div className="pagination">
          <button className="page-btn" disabled={page === 1} onClick={() => goTo(page - 1)} title="Previous page">
            <ChevronLeft size={18} />
          </button>

          <div className="page-nums">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                className={"page-btn" + (p === page ? " active" : "")}
                onClick={() => goTo(p)}
              >
                {p}
              </button>
            ))}
          </div>

          <span className="page-info">Page {page} of {totalPages}</span>

          <button className="page-btn" disabled={page === totalPages} onClick={() => goTo(page + 1)} title="Next page">
            <ChevronRight size={18} />
          </button>
        </div>
      )}

      {selected && (
        <TradeModal
          stock={selected}
          portfolio={portfolio}
          onClose={() => setSelected(null)}
          onDone={loadPortfolio}
        />
      )}
    </>
  );
}
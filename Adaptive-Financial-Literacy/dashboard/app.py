import os
from dotenv import load_dotenv
from pymongo import MongoClient
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.graph_objects as go
from datetime import datetime
from bson import ObjectId
import json

# backend ki .env se hi DB ka address uthate hain
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

WEAK_BELOW = 60  # backend ke weak-topic rule jaisa
GREEN, CYAN, AMBER, RED = "#10b981", "#06b6d4", "#fbbf24", "#f87171"
TEXT, MUTED, SLATE = "#e8edf7", "#8b97b1", "#475569"
RISK_COLORS = {"Conservative": CYAN, "Moderate": GREEN, "Aggressive": AMBER, "Not set": SLATE}


def pretty(topic):
    return topic.replace("_", " ").title()


def load_data():
    students = list(db.students.find())
    attempts = db.attempts.count_documents({})

    rows, topic_scores, risk_counts = [], {}, {}
    total_modules, diagnostic_done, student_avgs = 0, 0, []

    for s in students:
        scores = s.get("topic_scores", {})
        percents = {t: v["percent"] for t, v in scores.items() if "percent" in v}

        avg = round(sum(percents.values()) / len(percents)) if percents else None
        if avg is not None:
            student_avgs.append(avg)
        weak = [pretty(t) for t, p in percents.items() if p < WEAK_BELOW]
        for t, p in percents.items():
            topic_scores.setdefault(t, []).append(p)

        profile = s.get("risk_profile") or "Not set"
        risk_counts[profile] = risk_counts.get(profile, 0) + 1
        done = len(s.get("completed_modules", []))
        total_modules += done
        diagnostic_done += 1 if s.get("diagnostic_done") else 0

        rows.append({
            "id": str(s["_id"]),
            "name": s.get("name", ""),
            "email": s.get("email", ""),
            "risk_profile": profile,
            "diagnostic": "Yes" if s.get("diagnostic_done") else "No",
            "avg_mastery": f"{avg}%" if avg is not None else "-",
            "modules_done": done,
            "weak_topics": ", ".join(weak) if weak else "-",
        })

    rows.sort(key=lambda r: r["name"].lower())
    topic_avg = {t: round(sum(v) / len(v)) for t, v in topic_scores.items()}
    class_avg = round(sum(student_avgs) / len(student_avgs)) if student_avgs else None

    return {
        "total": len(students),
        "diagnostic_done": diagnostic_done,
        "class_avg": class_avg,
        "modules": total_modules,
        "attempts": attempts,
        "rows": rows,
        "topic_avg": topic_avg,
        "risk_counts": risk_counts,
    }


# ---------- UI helpers ----------
def stat_card(label, value, sub=""):
    return html.Div(className="card", children=[
        html.Div(label, className="label"),
        html.Div(value, className="value"),
        html.Div(sub, className="sub"),
    ])


def style_fig(fig, height=330):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT),
        showlegend=False,
    )
    return fig


def empty_fig(message):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(color=MUTED, size=15))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style_fig(fig)


def topic_figure(topic_avg):
    if not topic_avg:
        return empty_fig("No diagnostic data yet")
    topics = list(topic_avg.keys())
    values = [topic_avg[t] for t in topics]
    colors = [RED if v < WEAK_BELOW else (AMBER if v < 80 else GREEN) for v in values]
    fig = go.Figure(go.Bar(
        x=[pretty(t) for t in topics],
        y=values,
        marker_color=colors,
        text=[f"{v}%" for v in values],
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_yaxes(range=[0, 110], gridcolor="rgba(148,163,184,0.12)", ticksuffix="%")
    fig.update_xaxes(showgrid=False, linecolor="rgba(148,163,184,0.3)")
    return style_fig(fig)


def risk_figure(risk_counts):
    if not risk_counts:
        return empty_fig("No students yet")
    labels = list(risk_counts.keys())
    fig = go.Figure(go.Pie(
        labels=labels,
        values=[risk_counts[k] for k in labels],
        hole=0.62,
        marker=dict(colors=[RISK_COLORS.get(k, SLATE) for k in labels]),
        textinfo="value",
    ))
    fig.update_layout(showlegend=True, legend=dict(font=dict(color=TEXT)))
    return style_fig(fig)


TABLE_STYLES = dict(
    style_table={"overflowX": "auto"},
    style_header={
        "backgroundColor": "rgba(255,255,255,0.05)", "color": MUTED,
        "fontWeight": "600", "border": "none", "textTransform": "uppercase", "fontSize": "12px",
    },
    style_cell={
        "backgroundColor": "transparent", "color": TEXT, "border": "none",
        "borderBottom": "1px solid rgba(148,163,184,0.14)",
        "padding": "12px 10px", "fontFamily": "Inter, sans-serif", "fontSize": "14px",
        "textAlign": "left",
    },
)


def trend_figure():
    attempts = list(db.attempts.find({"passed": {"$exists": True}}))
    if not attempts:
        return empty_fig("No quiz attempts yet")

    per_day = {}
    for a in attempts:
        day = str(a.get("time", ""))[:10]
        if not day:
            continue
        d = per_day.setdefault(day, {"n": 0, "passed": 0})
        d["n"] += 1
        d["passed"] += 1 if a.get("passed") else 0

    days = sorted(per_day)
    counts = [per_day[d]["n"] for d in days]
    rates = [round(100 * per_day[d]["passed"] / per_day[d]["n"]) for d in days]

    fig = go.Figure()
    fig.add_bar(x=days, y=counts, name="Attempts", marker_color=GREEN)
    fig.add_scatter(
        x=days, y=rates, name="Pass rate", yaxis="y2",
        mode="lines+markers", line=dict(color=AMBER, width=3),
    )
    fig = style_fig(fig)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=1.15, font=dict(color=TEXT)),
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(gridcolor="rgba(148,163,184,0.12)", rangemode="tozero"),
        yaxis2=dict(overlaying="y", side="right", range=[0, 100], ticksuffix="%", showgrid=False),
    )
    fig.update_xaxes(type="category", showgrid=False, linecolor="rgba(148,163,184,0.3)")
    return fig


def module_figure():
    titles = {m["id"]: m["title"] for m in db.modules.find({}, {"id": 1, "title": 1})}
    stats = {}
    for a in db.attempts.find({"module_id": {"$exists": True}}):
        s = stats.setdefault(a["module_id"], {"n": 0, "passed": 0})
        s["n"] += 1
        s["passed"] += 1 if a.get("passed") else 0

    if not stats:
        return empty_fig("No module quiz data yet")

    rows = sorted(
        ((titles.get(mid, f"Module {mid}"), round(100 * s["passed"] / s["n"]), s["n"]) for mid, s in stats.items()),
        key=lambda r: r[1],
    )
    names = [r[0] for r in rows]
    rates = [r[1] for r in rows]
    colors = [RED if v < 50 else (AMBER if v < 75 else GREEN) for v in rates]

    fig = go.Figure(go.Bar(
        x=rates, y=names, orientation="h", marker_color=colors,
        text=[f"{r[1]}%  ({r[2]} attempts)" for r in rows],
        textposition="outside", cliponaxis=False,
    ))
    fig = style_fig(fig, height=max(330, 54 * len(names) + 90))
    fig.update_xaxes(range=[0, 150], tickvals=[0, 25, 50, 75, 100], ticksuffix="%", gridcolor="rgba(148,163,184,0.12)")
    fig.update_yaxes(autorange="reversed", automargin=True)
    return fig


def student_detail_view(student_id):
    try:
        s = db.students.find_one({"_id": ObjectId(student_id)})
    except Exception:
        s = None
    if not s:
        return html.P("Student not found.", className="hint")

    scores = {t: v["percent"] for t, v in s.get("topic_scores", {}).items() if "percent" in v}
    avg = round(sum(scores.values()) / len(scores)) if scores else None

    attempts = list(db.attempts.find({"student_id": student_id}).sort("time", -1))
    passed = sum(1 for a in attempts if a.get("passed"))
    pass_rate = f"{round(100 * passed / len(attempts))}%" if attempts else "-"
    titles = {m["id"]: m["title"] for m in db.modules.find({}, {"id": 1, "title": 1})}

    rows = []
    for a in attempts[:10]:
        try:
            when = datetime.fromisoformat(a["time"]).strftime("%d %b, %H:%M")
        except Exception:
            when = "-"
        rows.append({
            "when": when,
            "module": titles.get(a.get("module_id"), "-"),
            "score": f'{a.get("quiz_percent", "-")}%',
            "result": "Passed" if a.get("passed") else "Retry",
        })

    if rows:
        attempts_view = dash_table.DataTable(
            data=rows,
            columns=[
                {"name": "When (UTC)", "id": "when"},
                {"name": "Module", "id": "module"},
                {"name": "Score", "id": "score"},
                {"name": "Result", "id": "result"},
            ],
            page_size=5,
            style_data_conditional=[
                {"if": {"column_id": "result", "filter_query": '{result} = "Passed"'}, "color": GREEN},
                {"if": {"column_id": "result", "filter_query": '{result} = "Retry"'}, "color": AMBER},
            ],
            **TABLE_STYLES,
        )
    else:
        attempts_view = html.P("No quiz attempts yet.", className="hint")

    return html.Div([
        html.Div(className="student-head", children=[
            html.Div([html.H2(s.get("name", "")), html.P(s.get("email", ""), className="hint")]),
            html.Div(className="chip-row", children=[
                html.Span(s.get("risk_profile") or "Risk: not set", className="pill"),
                html.Span("Diagnostic done" if s.get("diagnostic_done") else "Diagnostic pending", className="pill"),
            ]),
        ]),
        html.Div(className="cards mini", children=[
            stat_card("Avg mastery", f"{avg}%" if avg is not None else "-"),
            stat_card("Modules done", str(len(s.get("completed_modules", [])))),
            stat_card("Quiz attempts", str(len(attempts))),
            stat_card("Pass rate", pass_rate),
        ]),
        html.Div(className="charts even", children=[
            html.Div([
                html.H4("Topic mastery"),
                dcc.Graph(figure=topic_figure(scores), config={"displayModeBar": False}),
            ]),
            html.Div([html.H4("Recent quiz attempts"), attempts_view]),
        ]),
    ])


MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "model_weights.json")


def load_model_card():
    try:
        with open(MODEL_PATH) as f:
            meta = json.load(f)["meta"]
    except Exception:
        return html.P("Model file not found. Train it first with ml/train_model.py.", className="hint")

    logged = list(db.attempts.find(
        {"features": {"$exists": True}, "predicted_pass_prob": {"$ne": None}},
        {"passed": 1, "predicted_pass_prob": 1},
    ))
    n = len(logged)
    if n:
        predicted = round(100 * sum(a["predicted_pass_prob"] for a in logged) / n)
        actual = round(100 * sum(1 for a in logged if a.get("passed")) / n)
        note = f"Live check on {n} real attempts: model predicted a {predicted}% pass rate, actual was {actual}%."
        if n < 30:
            note += " (small sample, treat as indicative only)"
    else:
        note = "No real attempts logged yet. Take a module quiz in the student app to start the live check."

    auc = meta.get("test_auc")
    trained_on = "Synthetic + real" if "real" in meta.get("trained_on", "") else "Synthetic"
    return html.Div([
        html.Div(className="cards mini", children=[
            stat_card("Test accuracy", f'{round(meta["test_accuracy"] * 100)}%', f'baseline {round(meta["baseline_accuracy"] * 100)}%'),
            stat_card("Test AUC", str(auc) if auc is not None else "-", "hold-out data"),
            stat_card("Trained on", trained_on, f'{meta["n_samples"]} samples'),
            stat_card("Real attempts logged", str(n), "features saved for retraining"),
        ]),
        html.P(note, className="hint"),
    ])

# ---------- Layout ----------
app = Dash(__name__, title="FinLit Educator Dashboard")

app.layout = html.Div(className="dash-wrap", children=[
    html.Div(className="dash-head", children=[
        html.Div([
            html.H1("Educator Dashboard"),
            html.P("Class progress, weak topics and risk profiles at a glance."),
        ]),
        html.Span("Auto-refreshes every 15 seconds", className="live"),
    ]),

    html.Div(id="cards", className="cards"),

    html.Div(className="charts", children=[
        html.Div(className="panel", children=[
            html.H3("Class average mastery by topic"),
            dcc.Graph(id="topic-chart", config={"displayModeBar": False}),
        ]),
        html.Div(className="panel", children=[
            html.H3("Risk profiles"),
            dcc.Graph(id="risk-chart", config={"displayModeBar": False}),
        ]),
    ]),

        html.Div(className="charts even", children=[
        html.Div(className="panel", children=[
            html.H3("Quiz activity and pass rate"),
            dcc.Graph(id="trend-chart", config={"displayModeBar": False}),
        ]),
        html.Div(className="panel", children=[
            html.H3("Module pass rate (hardest first)"),
            dcc.Graph(id="module-chart", config={"displayModeBar": False}),
        ]),
    ]),

    html.Div(className="panel", children=[
        html.H3("Students"),
        html.P("Click any row to see that student's details below.", className="hint"),
                html.Div(className="table-tools", children=[
            dcc.Input(
                id="student-search",
                type="search",
                placeholder="Search by name, email, risk profile or weak topic",
                className="search-input",
                autoComplete="off",
            ),
            html.Span(id="search-count", className="result-note"),
        ]),
        dash_table.DataTable(
            id="students-table",
            columns=[
                {"name": "Student", "id": "name"},
                {"name": "Email", "id": "email"},
                {"name": "Risk profile", "id": "risk_profile"},
                {"name": "Diagnostic", "id": "diagnostic"},
                {"name": "Avg mastery", "id": "avg_mastery"},
                {"name": "Modules done", "id": "modules_done"},
                {"name": "Weak topics", "id": "weak_topics"},
            ],
            data=[],
            page_size=8,
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "rgba(255,255,255,0.05)", "color": MUTED,
                "fontWeight": "600", "border": "none", "textTransform": "uppercase", "fontSize": "12px",
            },
            style_cell={
                "backgroundColor": "transparent", "color": TEXT, "border": "none",
                "borderBottom": "1px solid rgba(148,163,184,0.14)",
                "padding": "14px 12px", "fontFamily": "Inter, sans-serif", "fontSize": "14px",
                "textAlign": "left",
            },
            style_data_conditional=[
                {"if": {"column_id": "weak_topics", "filter_query": '{weak_topics} != "-"'}, "color": AMBER},
                {"if": {"state": "active"}, "backgroundColor": "rgba(16,185,129,0.15)", "border": "1px solid #10b981"},
            ],
        ),
        html.Div(className="panel", children=[
        html.H3("Student detail"),
        html.Div(id="drill"),
    ]),
    ]),

    dcc.Interval(id="tick", interval=15000, n_intervals=0),
    dcc.Store(id="students-store"),
    html.P("Educational purpose only. Not financial advice.", className="foot"),
])


@app.callback(
    Output("cards", "children"),
    Output("topic-chart", "figure"),
    Output("risk-chart", "figure"),
    Output("students-store", "data"),
    Output("trend-chart", "figure"),
    Output("module-chart", "figure"),
    Input("tick", "n_intervals"),
)
def refresh(_):
    d = load_data()

    percent_done = round(100 * d["diagnostic_done"] / d["total"]) if d["total"] else 0
    cards = [
        stat_card("Total students", str(d["total"])),
        stat_card("Diagnostic completed", f'{d["diagnostic_done"]} / {d["total"]}', f"{percent_done}% of class"),
        stat_card("Class avg mastery", f'{d["class_avg"]}%' if d["class_avg"] is not None else "-", "across all topics"),
        stat_card("Modules completed", str(d["modules"]), "total across students"),
        stat_card("Quiz attempts", str(d["attempts"]), "module quizzes taken"),
    ]
    return (
        cards,
        topic_figure(d["topic_avg"]),
        risk_figure(d["risk_counts"]),
        d["rows"],
        trend_figure(),
        module_figure(),
    )


@app.callback(
    Output("drill", "children"),
    Input("students-table", "active_cell"),
    Input("tick", "n_intervals"),
)
def show_student(active_cell, _):
    if not active_cell or not active_cell.get("row_id"):
        return html.P("Click any student row in the table above to see their details.", className="hint")
    return student_detail_view(active_cell["row_id"])




@app.callback(
    Output("students-table", "data"),
    Output("search-count", "children"),
    Input("students-store", "data"),
    Input("student-search", "value"),
)
def filter_students(rows, query):
    rows = rows or []
    total = len(rows)
    q = (query or "").strip().lower()
    if q:
        rows = [
            r for r in rows
            if q in " ".join(str(r[k]) for k in ("name", "email", "risk_profile", "weak_topics")).lower()
        ]
    return rows, f"Showing {len(rows)} of {total} students"


@app.callback(Output("model-card", "children"), Input("tick", "n_intervals"))
def refresh_model_card(_):
    return load_model_card()



if __name__ == "__main__":
    app.run(debug=True , dev_tools_ui=False)
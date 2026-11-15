import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, CheckCircle2, Gauge, BookOpen, Trophy } from "lucide-react";
import { api } from "../api";
import { useStudent } from "../StudentContext";
import { prettyTopic } from "../utils";

const DIFF_BADGE = { easy: "green", medium: "amber", hard: "red" };
const cleanReason = (text) => text.replace(/_/g, " ");

export default function LearningPath() {
  const { student } = useStudent();
  const [data, setData] = useState(null);
  const [modules, setModules] = useState([]);
  const [error, setError] = useState("");

  const completedIds = student.completed_modules || [];

  useEffect(() => {
    if (!student.diagnostic_done) return;
    Promise.all([api.getLearningPath(student._id), api.listModules()])
      .then(([path, mods]) => {
        setData(path);
        setModules(mods);
      })
      .catch((e) => setError(e.message));
  }, [student._id, student.diagnostic_done, student.completed_modules]);

  if (!student.diagnostic_done) {
    return (
      <>
        <div className="page-head">
          <h1>Your Learning Path</h1>
          <p>Personalised lessons, built around you.</p>
        </div>
        <div className="card coming">
          <p style={{ marginBottom: 18 }}>Take the diagnostic quiz first so we know where to start.</p>
          <Link to="/diagnostic" className="btn btn-primary">
            Take diagnostic quiz <ArrowRight size={18} />
          </Link>
        </div>
      </>
    );
  }

  if (error) return <div className="error-text">{error}</div>;
  if (!data) return <div className="card coming">Building your path...</div>;

  const next = data.path[0];
  const rest = data.path.slice(1);
  const completed = modules.filter((m) => completedIds.includes(m.id));

  return (
    <>
      <div className="page-head">
        <h1>Your Learning Path</h1>
        <p>
          Personalised for your {data.risk_profile || "learning"} profile and your weak topics.
        </p>
      </div>

      <div className="grid-3">
        <div className="card stat">
          <div className="stat-icon"><Gauge size={24} /></div>
          <div>
            <div className="stat-label">Your pace</div>
            <div className="stat-value" style={{ textTransform: "capitalize" }}>{data.pace}</div>
          </div>
        </div>
        <div className="card stat">
          <div className="stat-icon"><BookOpen size={24} /></div>
          <div>
            <div className="stat-label">Modules per session</div>
            <div className="stat-value">{data.modules_per_session}</div>
          </div>
        </div>
        <div className="card stat">
          <div className="stat-icon"><Trophy size={24} /></div>
          <div>
            <div className="stat-label">Completed</div>
            <div className="stat-value">{completed.length} / {modules.length}</div>
          </div>
        </div>
      </div>

      {next ? (
        <div className="card up-next">
          <div className="eyebrow">Up next</div>
          <h2>{next.title}</h2>
          <div className="badge-row">
            <span className="badge">{prettyTopic(next.topic)}</span>
            <span className={"badge " + DIFF_BADGE[next.difficulty]}>{next.difficulty}</span>
            {next.pass_probability != null && (
              <span className="badge">Predicted success: {next.pass_probability}%</span>
            )}
          </div>
          <p className="reason">Why this module: {cleanReason(next.reason)}.</p>
          <Link to={`/learn/${next.id}`} className="btn btn-primary">
            Start module <ArrowRight size={18} />
          </Link>
        </div>
      ) : (
        <div className="card coming">You have completed every module. Great work! 🎉</div>
      )}

      {rest.length > 0 && (
        <>
          <div className="section-title">Coming up</div>
          <div className="path-list">
            {rest.map((m, i) => (
              <Link key={m.id} to={`/learn/${m.id}`} className="path-item">
                <div className="path-num">{i + 2}</div>
                <div className="path-body">
                  <h3>{m.title}</h3>
                  <p>{cleanReason(m.reason)}</p>
                </div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
                  {m.pass_probability != null && (
                    <span className="badge">{m.pass_probability}% success</span>
                  )}
                  <span className={"badge " + DIFF_BADGE[m.difficulty]}>{m.difficulty}</span>
                </div>
              </Link>
            ))}
          </div>
        </>
      )}

      {completed.length > 0 && (
        <>
          <div className="section-title">Completed</div>
          <div className="path-list">
            {completed.map((m) => (
              <Link key={m.id} to={`/learn/${m.id}`} className="path-item completed">
                <div className="path-num"><CheckCircle2 size={20} /></div>
                <div className="path-body">
                  <h3>{m.title}</h3>
                  <p>{prettyTopic(m.topic)}</p>
                </div>
                <span className={"badge " + DIFF_BADGE[m.difficulty]}>{m.difficulty}</span>
              </Link>
            ))}
          </div>
        </>
      )}
    </>
  );
}
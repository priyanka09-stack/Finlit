import { Link } from "react-router-dom";
import {
  CheckCircle2,
  Circle,
  ChevronRight,
  ShieldCheck,
  BarChart3,
  Trophy,
} from "lucide-react";
import { useStudent } from "../StudentContext";

export default function Dashboard() {
  const { student } = useStudent();

  const steps = [
    {
      title: "Take the risk profile quiz",
      text: "Tell us how you feel about risk so lessons can be personalised.",
      done: !!student.risk_profile,
      to: "/risk-quiz",
      enabled: true,
    },
    {
      title: "Take the diagnostic quiz",
      text: "A quick check of what you already know, topic by topic.",
      done: !!student.diagnostic_done,
      to: "/diagnostic",
      enabled: true,
    },
    {
      title: "Follow your learning path",
      text: "Modules picked for your weak areas and risk profile.",
      done: (student.completed_modules || []).length > 0,
      to: "/learn",
      enabled: !!student.diagnostic_done,
    },
  ];

  const doneCount = steps.filter((s) => s.done).length;
  const percent = Math.round((100 * doneCount) / steps.length);
  const topicsAssessed = Object.keys(student.topic_scores || {}).length;

  return (
    <>
      <div className="page-head">
        <h1>Welcome, {student.name} ❤️</h1>
        <p>Here is where you stand today.</p>
      </div>

      <div className="grid-3">
        <div className="card stat">
          <div className="stat-icon">
            <ShieldCheck size={24} />
          </div>
          <div>
            <div className="stat-label">Risk profile</div>
            <div className="stat-value">
              {student.risk_profile || "Not set"}
            </div>
          </div>
        </div>

        <div className="card stat">
          <div className="stat-icon">
            <BarChart3 size={24} />
          </div>
          <div>
            <div className="stat-label">Topics assessed</div>
            <div className="stat-value">{topicsAssessed}</div>
          </div>
        </div>

        <div className="card stat">
          <div className="stat-icon">
            <Trophy size={24} />
          </div>
          <div>
            <div className="stat-label">Modules completed</div>
            <div className="stat-value">
              {(student.completed_modules || []).length}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: 10,
          }}
        >
          <strong>Getting started</strong>
          <span className="badge">{percent}% done</span>
        </div>

        <div className="progress">
          <div
            className="progress-bar"
            style={{ width: `${percent}%` }}
          />
        </div>

        <div className="steps">
          {steps.map((s) => (
            <Link
              key={s.title}
              to={s.to}
              className={
                "step" +
                (s.done ? " done" : "") +
                (s.enabled ? "" : " locked")
              }
            >
              {s.done ? (
                <CheckCircle2 className="step-icon" size={26} />
              ) : (
                <Circle className="step-icon" size={26} />
              )}

              <div className="step-body">
                <h3>{s.title}</h3>
                <p>{s.text}</p>
              </div>

              <ChevronRight className="step-arrow" size={20} />
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}

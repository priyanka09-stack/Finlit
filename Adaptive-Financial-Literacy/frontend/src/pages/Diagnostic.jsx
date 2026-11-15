import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Target, ArrowRight } from "lucide-react";
import { api } from "../api";
import { useStudent } from "../StudentContext";
import { prettyTopic } from "../utils";
import QuizFlow from "../components/QuizFlow";

function barClass(percent) {
  if (percent >= 80) return "";
  if (percent >= 60) return "mid";
  return "weak";
}

export default function Diagnostic() {
  const { student, refresh } = useStudent();
  const [questions, setQuestions] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.getDiagnostic().then(setQuestions).catch((e) => setError(e.message));
  }, []);

  async function finish(answers) {
    setBusy(true);
    setError("");
    try {
      const res = await api.submitDiagnostic(student._id, answers);
      await refresh();
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="narrow">
      <div className="page-head">
        <h1>Diagnostic Quiz</h1>
        <p>A quick check of what you already know. No pressure, it only shapes your lessons.</p>
      </div>

      {error && <div className="error-text">{error}</div>}

      {result ? (
        <div className="card result">
          <div className="result-icon"><Target size={36} /></div>
          <span className="badge">Your results</span>
          <h2>Here is where you stand</h2>

          <div className="score-list">
            {Object.entries(result.topic_scores).map(([topic, s]) => (
              <div key={topic}>
                <div className="score-head">
                  <span>{prettyTopic(topic)}</span>
                  <span>{s.correct}/{s.total} correct ({s.percent}%)</span>
                </div>
                <div className="progress">
                  <div className={"progress-bar " + barClass(s.percent)} style={{ width: `${s.percent}%` }} />
                </div>
              </div>
            ))}
          </div>

          {result.weak_topics.length > 0 ? (
            <>
              <p>We will start your lessons with these focus areas:</p>
              <div className="focus-row">
                {result.weak_topics.map((t) => (
                  <span key={t} className="badge amber">{prettyTopic(t)}</span>
                ))}
              </div>
            </>
          ) : (
            <p>Great start! No weak areas found, so your path will move at a faster pace.</p>
          )}

          <div className="result-actions">
            <Link to="/learn" className="btn btn-primary">
              See my learning path <ArrowRight size={18} />
            </Link>
            <Link to="/" className="btn btn-ghost">Back to dashboard</Link>
          </div>
        </div>
      ) : questions ? (
        <QuizFlow questions={questions} onFinish={finish} busy={busy} />
      ) : (
        !error && <div className="card coming">Loading questions...</div>
      )}
    </div>
  );
}
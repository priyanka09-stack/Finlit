import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowRight, CheckCircle2, RotateCcw } from "lucide-react";
import { api } from "../api";
import { useStudent } from "../StudentContext";
import { prettyTopic } from "../utils";
import QuizFlow from "../components/QuizFlow";

export default function ModuleQuiz() {
  const { id } = useParams();
  const { student, refresh } = useStudent();
  const [questions, setQuestions] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    setQuestions(null);
    setResult(null);
    api.getModuleQuiz(id).then(setQuestions).catch((e) => setError(e.message));
  }, [id]);

  async function finish(answers) {
    setBusy(true);
    setError("");
    try {
      const res = await api.submitModuleQuiz(student._id, id, answers);
      await refresh();
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  function retry() {
    setResult(null);
    setAttempt((a) => a + 1);
  }

  return (
    <div className="narrow">
      <Link to={`/learn/${id}`} className="back-link">
        <ArrowLeft size={16} /> Back to module
      </Link>

      <div className="page-head">
        <h1>Module Quiz</h1>
        <p>Two quick questions to check what you picked up.</p>
      </div>

      {error && <div className="error-text">{error}</div>}

      {result ? (
        <div className="card result">
          <div className="result-icon" style={result.passed ? {} : { background: "var(--amber)" }}>
            {result.passed ? <CheckCircle2 size={36} /> : <RotateCcw size={36} />}
          </div>
          <span className={"badge " + (result.passed ? "green" : "amber")}>
            Quiz score: {result.quiz_percent}%
          </span>
          <h2>{result.passed ? "Module completed!" : "Not quite there yet"}</h2>
          <p>
            {result.passed
              ? "Nicely done. Your progress has been updated and your path adjusted."
              : "No worries. Re-read the module and try again, it will stay in your path."}
          </p>

          <div className="mastery">
            <div className="score-head">
              <span>{prettyTopic(result.topic)} mastery</span>
              <span>{result.topic_percent_before}% → {result.topic_percent_after}%</span>
            </div>
            <div className="progress">
              <div
                className={"progress-bar " + (result.topic_percent_after >= 60 ? "" : "weak")}
                style={{ width: `${result.topic_percent_after}%` }}
              />
            </div>
          </div>

          <div className="result-actions">
            {result.passed ? (
              <>
                {result.next_module && (
                  <Link to={`/learn/${result.next_module.id}`} className="btn btn-primary">
                    Next: {result.next_module.title} <ArrowRight size={18} />
                  </Link>
                )}
                <Link to="/learn" className="btn btn-ghost">Back to path</Link>
              </>
            ) : (
              <>
                <Link to={`/learn/${id}`} className="btn btn-primary">Re-read module</Link>
                <button className="btn btn-ghost" onClick={retry}>Try again</button>
              </>
            )}
          </div>
        </div>
      ) : questions ? (
        <QuizFlow key={attempt} questions={questions} onFinish={finish} busy={busy} />
      ) : (
        !error && <div className="card coming">Loading quiz...</div>
      )}
    </div>
  );
}
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, ArrowRight } from "lucide-react";
import { api } from "../api";
import { useStudent } from "../StudentContext";
import QuizFlow from "../components/QuizFlow";

const PROFILE_INFO = {
  Conservative: "You prefer stability and protecting your money over chasing high returns.",
  Moderate: "You are comfortable with some ups and downs in exchange for steady growth.",
  Aggressive: "You are comfortable with big swings in the hope of higher returns.",
};

export default function RiskQuiz() {
  const { student, refresh } = useStudent();
  const [questions, setQuestions] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.getRiskQuiz().then(setQuestions).catch((e) => setError(e.message));
  }, []);

  async function finish(answers) {
    setBusy(true);
    setError("");
    try {
      const res = await api.submitRiskQuiz(student._id, answers);
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
        <h1>Risk Profile Quiz</h1>
        <p>
          {student.risk_profile
            ? `Your current profile is ${student.risk_profile}. Retake anytime, your learning path will adjust.`
            : "5 quick questions to understand how you feel about risk."}
        </p>
      </div>

      {error && <div className="error-text">{error}</div>}

      {result ? (
        <div className="card result">
          <div className="result-icon"><ShieldCheck size={36} /></div>
          <span className="badge">Your risk profile</span>
          <h2 className="grad">{result.risk_profile}</h2>
          <p>{PROFILE_INFO[result.risk_profile]}</p>
          <div className="result-actions">
            <Link to="/diagnostic" className="btn btn-primary">
              Next: diagnostic quiz <ArrowRight size={18} />
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
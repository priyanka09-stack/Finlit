import { useState } from "react";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { prettyTopic } from "../utils";

export default function QuizFlow({ questions, onFinish, busy }) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState(Array(questions.length).fill(null));

  const q = questions[index];
  const isLast = index === questions.length - 1;
  const selected = answers[index];

  function choose(i) {
    const next = [...answers];
    next[index] = i;
    setAnswers(next);
  }

  return (
    <div className="card quiz">
      <div className="quiz-top">
        <span className="badge">
          Question {index + 1} of {questions.length}
        </span>
        {q.topic && <span className="quiz-topic">{prettyTopic(q.topic)}</span>}
      </div>

      <div className="progress">
        <div className="progress-bar" style={{ width: `${((index + 1) / questions.length) * 100}%` }} />
      </div>

      <h2 className="quiz-question">{q.question}</h2>

      <div className="options">
        {q.options.map((opt, i) => (
          <button
            key={i}
            type="button"
            className={"option" + (selected === i ? " selected" : "")}
            onClick={() => choose(i)}
          >
            <span className="option-letter">{"ABCD"[i]}</span>
            <span>{opt}</span>
          </button>
        ))}
      </div>

      <div className="quiz-actions">
        <button className="btn btn-ghost" disabled={index === 0} onClick={() => setIndex(index - 1)}>
          <ArrowLeft size={18} /> Back
        </button>

        {isLast ? (
          <button className="btn btn-primary" disabled={selected === null || busy} onClick={() => onFinish(answers)}>
            {busy ? "Submitting..." : "Finish"} <Check size={18} />
          </button>
        ) : (
          <button className="btn btn-primary" disabled={selected === null} onClick={() => setIndex(index + 1)}>
            Next <ArrowRight size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { api } from "../api";
import { prettyTopic } from "../utils";

const DIFF_BADGE = { easy: "green", medium: "amber", hard: "red" };

export default function ModulePage() {
  const { id } = useParams();
  const [mod, setMod] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setMod(null);
    api.getModule(id).then(setMod).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <div className="error-text">{error}</div>;
  if (!mod) return <div className="card coming">Loading module...</div>;

  const words = mod.content.join(" ").split(/\s+/).length;
  const minutes = Math.max(1, Math.round(words / 200));

  return (
    <div className="narrow">
      <Link to="/learn" className="back-link">
        <ArrowLeft size={16} /> Back to learning path
      </Link>

      <div className="page-head">
        <h1>{mod.title}</h1>
        <div className="badge-row" style={{ marginTop: 12 }}>
          <span className="badge">{prettyTopic(mod.topic)}</span>
          <span className={"badge " + DIFF_BADGE[mod.difficulty]}>{mod.difficulty}</span>
          <span className="badge">{minutes} min read</span>
        </div>
      </div>

      <div className="card reader">
        {mod.content.map((para, i) => (
          <p key={i}>{para}</p>
        ))}

        <div className="reader-footer">
          <span>Finished reading? Check what you learned.</span>
          <Link to={`/learn/${mod.id}/quiz`} className="btn btn-primary">
            Take the module quiz <ArrowRight size={18} />
          </Link>
        </div>
      </div>
    </div>
  );
}
import { useState } from "react";
import { KeyRound, UserRound } from "lucide-react";
import { api } from "../api";
import { useStudent } from "../StudentContext";

export default function Profile() {
  const { student } = useStudent();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setDone("");
    if (next.length < 6) return setError("New password must be at least 6 characters");
    if (next !== confirm) return setError("New passwords do not match");

    setBusy(true);
    try {
      await api.changePassword(student._id, current, next);
      setDone("Password updated successfully.");
      setCurrent("");
      setNext("");
      setConfirm("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const joined = student.created_at ? new Date(student.created_at).toLocaleDateString() : "-";

  return (
    <div className="narrow">
      <div className="page-head">
        <h1>My Profile</h1>
        <p>Your account details and security.</p>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-title"><UserRound size={20} /> Account</div>
        <div className="sum-row"><span>Name</span><strong>{student.name}</strong></div>
        <div className="sum-row"><span>Email</span><strong>{student.email}</strong></div>
        <div className="sum-row">
          <span>Risk profile</span>
          <span className="badge">{student.risk_profile || "Not set"}</span>
        </div>
        <div className="sum-row"><span>Joined</span><span>{joined}</span></div>
      </div>

      <form className="card" onSubmit={submit}>
        <div className="card-title"><KeyRound size={20} /> Change password</div>

        {error && <div className="error-text">{error}</div>}
        {done && <div className="success-text">{done}</div>}

        <div className="field">
          <label htmlFor="cur">Current password</label>
          <input id="cur" type="password" value={current} onChange={(e) => setCurrent(e.target.value)} required />
        </div>
        <div className="field">
          <label htmlFor="new">New password</label>
          <input id="new" type="password" value={next} onChange={(e) => setNext(e.target.value)} placeholder="At least 6 characters" required />
        </div>
        <div className="field">
          <label htmlFor="conf">Confirm new password</label>
          <input id="conf" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
        </div>

        <button className="btn btn-primary" disabled={busy}>
          {busy ? "Updating..." : "Update password"}
        </button>
      </form>
    </div>
  );
}
import { useState } from "react";
import { GraduationCap, ArrowRight, Target, LineChart, ShieldCheck, Eye, EyeOff } from "lucide-react";
import { useStudent } from "../StudentContext";

export default function Welcome() {
  const { login, register } = useStudent();
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const isLogin = mode === "login";

  function switchMode() {
    setMode(isLogin ? "register" : "login");
    setError("");
  }

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (isLogin) await login(email.trim(), password);
      else await register(name.trim(), email.trim(), password);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="welcome">
      <section className="welcome-hero">
        <div className="brand">
          <GraduationCap size={28} />
          <span>FinLit Simulator</span>
        </div>
        <h1>
          Learn investing <span className="grad">at your own pace.</span>
        </h1>
        <p>
          A simulator that understands what you know, how much risk you can handle, and
          builds your lessons around you.
        </p>
        <ul className="hero-points">
          <li><Target size={20} /> Lessons personalised to your weak topics</li>
          <li><LineChart size={20} /> Practise with real market prices, zero real risk</li>
          <li><ShieldCheck size={20} /> Feedback that matches your risk profile</li>
        </ul>
      </section>

      <section className="welcome-form">
        <form className="card welcome-card" onSubmit={submit}>
          <h2>{isLogin ? "Welcome back" : "Create your account"}</h2>
          <p>{isLogin ? "Log in to continue learning." : "It takes less than a minute."}</p>

          {error && <div className="error-text">{error}</div>}

          {!isLogin && (
            <div className="field">
              <label htmlFor="name">Name</label>
              <input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" required />
            </div>
          )}

          <div className="field">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <div className="pw-wrap">
              <input
                id="password"
                type={show ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={isLogin ? "Your password" : "At least 6 characters"}
                minLength={isLogin ? undefined : 6}
                required
              />
              <button type="button" className="pw-toggle" onClick={() => setShow(!show)} title={show ? "Hide" : "Show"}>
                {show ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Please wait..." : isLogin ? "Log in" : "Create account"} <ArrowRight size={18} />
          </button>

          <p className="hint">
            {isLogin ? "New here? " : "Already have an account? "}
            <button type="button" className="link-btn" onClick={switchMode}>
              {isLogin ? "Create an account" : "Log in"}
            </button>
          </p>
        </form>
      </section>
    </div>
  );
}
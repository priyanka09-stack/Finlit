

import { useState, useEffect } from "react";
import { NavLink, Outlet, useLocation, Link } from "react-router-dom";
import {
  LayoutDashboard, BookOpen, TrendingUp, Wallet, LogOut, GraduationCap, ChevronDown, UserRound,
} from "lucide-react";
import { useStudent } from "../StudentContext";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/learn", label: "Learn", icon: BookOpen },
  { to: "/market", label: "Market", icon: TrendingUp },
  { to: "/portfolio", label: "Portfolio", icon: Wallet },
];

export default function Layout() {
  const { student, logout } = useStudent();
  const [menuOpen, setMenuOpen] = useState(false);
    const location = useLocation();

  // page badalte hi profile menu band ho jaye
  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);
  const initial = student.name.charAt(0).toUpperCase();
  const profileText = student.risk_profile ? `${student.risk_profile} investor` : "Profile pending";

  return (
    <div className="shell">
            {menuOpen && <div className="menu-overlay" onClick={() => setMenuOpen(false)} />}
      {/* Mobile top bar (desktop pe hidden) */}
      <header className="topbar">
        <div className="topbar-brand">
          <GraduationCap size={22} />
          <span>FinLit</span>
        </div>
        <button className="profile-btn" onClick={() => setMenuOpen(!menuOpen)}>
          <div className="avatar">{initial}</div>
          <ChevronDown size={16} className={menuOpen ? "flip" : ""} />
        </button>

        {menuOpen && (
          <div className="profile-menu">
            <strong>{student.name}</strong>
            <small>{student.email}</small>
            <span className="badge">{profileText}</span>
                        <Link to="/profile" className="btn btn-ghost">
              <UserRound size={16} /> My profile
            </Link>
            <button className="btn btn-ghost" onClick={logout}>
              <LogOut size={16} /> Log out
            </button>
          </div>
        )}
      </header>

      <aside className="sidebar">
        <div className="brand">
          <GraduationCap size={26} />
          <span>FinLit Simulator</span>
        </div>

        <nav className="nav">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              <Icon size={20} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="user-box">
          <div className="avatar">{initial}</div>
          <Link to="/profile" className="user-info" title="My profile">
            <strong>{student.name}</strong>
            <small>{profileText}</small>
          </Link>
          <button className="icon-btn" onClick={logout} title="Log out">
            <LogOut size={18} />
          </button>
        </div>
      </aside>

      <main className="content">
        <Outlet />
        <footer className="disclaimer">
          Educational purpose only. Not financial advice. Market data is delayed and used for learning.
        </footer>
      </main>
    </div>
  );
}
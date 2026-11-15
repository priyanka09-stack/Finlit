import { Routes, Route, Navigate } from "react-router-dom";
import { useStudent } from "./StudentContext";
import Layout from "./components/Layout";
import Welcome from "./pages/Welcome";
import Dashboard from "./pages/Dashboard";
import ComingSoon from "./pages/ComingSoon";
import RiskQuiz from "./pages/RiskQuiz";
import Diagnostic from "./pages/Diagnostic";
import LearningPath from "./pages/LearningPath";
import ModulePage from "./pages/ModulePage";
import ModuleQuiz from "./pages/ModuleQuiz";
import Market from "./pages/Market";
import Portfolio from "./pages/Portfolio";
import Profile from "./pages/Profile";

export default function App() {
  const { student, loading } = useStudent();

  if (loading) return <div className="center-screen">Loading...</div>;
  if (!student) return <Welcome />;

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/risk-quiz" element={<RiskQuiz />} />
        <Route path="/diagnostic" element={<Diagnostic />} />
        <Route path="/learn" element={<LearningPath />} />
        <Route path="/learn/:id" element={<ModulePage />} />
        <Route path="/learn/:id/quiz" element={<ModuleQuiz />} />
        <Route path="/market" element={<Market />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
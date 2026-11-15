import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api, getToken, setToken } from "./api";

const StudentContext = createContext(null);

export function StudentProvider({ children }) {
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!getToken()) {
      setStudent(null);
      setLoading(false);
      return;
    }
    try {
      setStudent(await api.me());
    } catch (e) {
      if (e.status === 401) setToken(null); // token galat ya expire hai
      setStudent(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function login(email, password) {
    const res = await api.login(email, password);
    setToken(res.token);
    setStudent(res.student);
  }

  async function register(name, email, password) {
    const res = await api.register(name, email, password);
    setToken(res.token);
    setStudent(res.student);
  }

  function logout() {
    setToken(null);
    setStudent(null);
  }

  return (
    <StudentContext.Provider value={{ student, loading, login, register, logout, refresh }}>
      {children}
    </StudentContext.Provider>
  );
}

export const useStudent = () => useContext(StudentContext);
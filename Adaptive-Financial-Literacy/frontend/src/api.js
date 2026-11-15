const BASE = "http://127.0.0.1:5000/api";

const TOKEN_KEY = "finlit_token";
export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY));

async function request(path, options = {}) {
  const token = getToken();
  const res = await fetch(BASE + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  const data = await res.json().catch(() => null);
    // token expire ya galat ho gaya to seedha login page pe bhejo (login ki apni 401 ko chhodkar)
  if (res.status === 401 && token && path !== "/login") {
    setToken(null);
    window.location.reload();
    return new Promise(() => {});
  }
  if (!res.ok) {
    const err = new Error((data && data.error) || "Something went wrong");
    err.status = res.status;
    throw err;
  }
  if (data === null) throw new Error("Server sent an unexpected response");
  return data;
}

export const api = {
    register: (name, email, password) =>
    request("/students", { method: "POST", body: JSON.stringify({ name, email, password }) }),
  login: (email, password) =>
    request("/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => request("/me"),
  changePassword: (id, current_password, new_password) =>
    request(`/students/${id}/password`, {
      method: "POST",
      body: JSON.stringify({ current_password, new_password }),
    }),
    getRiskQuiz: () => request("/risk-quiz"),
  submitRiskQuiz: (id, answers) =>
    request(`/students/${id}/risk-quiz`, { method: "POST", body: JSON.stringify({ answers }) }),
  getDiagnostic: () => request("/diagnostic"),
  submitDiagnostic: (id, answers) =>
    request(`/students/${id}/diagnostic`, { method: "POST", body: JSON.stringify({ answers }) }),
    getLearningPath: (id) => request(`/students/${id}/learning-path`),
  listModules: () => request("/modules"),
  getModule: (mid) => request(`/modules/${mid}`),
  getModuleQuiz: (mid) => request(`/modules/${mid}/quiz`),
  submitModuleQuiz: (id, mid, answers) =>
    request(`/students/${id}/modules/${mid}/quiz`, { method: "POST", body: JSON.stringify({ answers }) }),
    getStocks: () => request("/market/stocks"),
  getMarketCondition: (simulate) =>
    request("/market/condition" + (simulate ? "?simulate=volatile" : "")),
  getPortfolio: (id) => request(`/students/${id}/portfolio`),
  trade: (id, symbol, quantity, action) =>
    request(`/students/${id}/trade`, { method: "POST", body: JSON.stringify({ symbol, quantity, action }) }),
    getPortfolioFeedback: (id) => request(`/students/${id}/portfolio-feedback`),
};
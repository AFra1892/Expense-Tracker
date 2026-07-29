import { createContext, useContext, useEffect, useState } from "react";
import { loginUser, registerUser, fetchCurrentUser } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On first load, if we have a stored token, try to fetch the user it belongs to.
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    fetchCurrentUser()
      .then(setUser)
      .catch(() => localStorage.removeItem("access_token"))
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const { access_token } = await loginUser(email, password);
    localStorage.setItem("access_token", access_token);
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
  }

  async function register(email, password) {
    await registerUser(email, password);
    await login(email, password);
  }

  function logout() {
    localStorage.removeItem("access_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}

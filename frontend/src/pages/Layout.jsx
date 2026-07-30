import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <nav className="navbar">
        <div className="navbar-links">
          <NavLink to="/transactions" className={({ isActive }) => (isActive ? "active" : "")}>
            Transactions
          </NavLink>
          <NavLink to="/charts" className={({ isActive }) => (isActive ? "active" : "")}>
            Charts
          </NavLink>
        </div>
        <div className="navbar-user">
          <span>{user?.email}</span>
          <button onClick={logout}>Log out</button>
        </div>
      </nav>
      <main className="page-content">
        <Outlet />
      </main>
    </div>
  );
}
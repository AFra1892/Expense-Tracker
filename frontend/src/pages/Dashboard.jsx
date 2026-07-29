import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="dashboard">
      <header>
        <h1>Dashboard</h1>
        <button onClick={logout}>Log out</button>
      </header>
      <p>Logged in as {user?.email}</p>
      <p>
        Transactions, categories, and charts land here in Phase 2 &mdash; this page is just
        confirming the auth flow works end to end.
      </p>
    </div>
  );
}

import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
} from "recharts";
import { fetchCategoryBreakdown, fetchMonthlyTotals } from "../api/reports";

const COLORS = ["#2563eb", "#16a34a", "#ea580c", "#9333ea", "#dc2626", "#0891b2", "#ca8a04", "#db2777", "#4b5563"];

export default function Charts() {
  const [byCategory, setByCategory] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchCategoryBreakdown(), fetchMonthlyTotals()])
      .then(([cat, month]) => {
        setByCategory(cat);
        setMonthly(month);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;

  const hasData = byCategory.length > 0 || monthly.length > 0;
  if (!hasData) {
    return <p className="empty-state">Add some categorized transactions to see charts here.</p>;
  }

  return (
    <div>
      <h1>Charts</h1>
      <section className="chart-section">
        <h2>Spending by category</h2>
        {byCategory.length === 0 ? (
          <p className="empty-state">No categorized transactions yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={byCategory}
                dataKey="total"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={110}
                label={(entry) => `${entry.category}: $${entry.total.toFixed(0)}`}
              >
                {byCategory.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )}
      </section>
      <section className="chart-section">
        <h2>Monthly totals</h2>
        {monthly.length === 0 ? (
          <p className="empty-state">No transactions yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
              <Bar dataKey="total" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>
    </div>
  );
}
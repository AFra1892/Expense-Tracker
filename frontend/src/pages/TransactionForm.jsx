import { useState } from "react";

const today = () => new Date().toISOString().slice(0, 10);

export default function TransactionForm({ categories, onCreate }) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState(today());
  const [categoryId, setCategoryId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await onCreate({
        description,
        amount: parseFloat(amount),
        date,
        category_id: categoryId || null,
      });
      setDescription("");
      setAmount("");
      setCategoryId("");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not add transaction");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="transaction-form">
      {error && <p className="error">{error}</p>}
      <input
        type="text"
        placeholder="Description (e.g. Trader Joe's)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <input
        type="number"
        step="0.01"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        required
      />
      <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
      <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
        <option value="">Uncategorized</option>
        {categories.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
      <button type="submit" disabled={submitting}>
        {submitting ? "Adding..." : "Add"}
      </button>
    </form>
  );
}
import CsvImport from "./CsvImport";
import { useEffect, useState } from "react";
import { fetchCategories } from "../api/categories";
import { fetchTransactions, createTransaction, updateTransaction, deleteTransaction } from "../api/transactions";
import TransactionForm from "./TransactionForm";
import TransactionList from "./TransactionList";
import AutoCategorizeButton from "./AutoCategorizeButton";

export default function Transactions() {
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [cats, txns] = await Promise.all([fetchCategories(), fetchTransactions()]);
      setCategories(cats);
      setTransactions(txns);
    } catch (err) {
      setError("Could not load data. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  async function refreshTransactions() {
  const txns = await fetchTransactions();
  setTransactions(txns);
}
  async function handleCreate(txnData) {
    const created = await createTransaction(txnData);
    setTransactions((prev) => [created, ...prev]);
  }

  async function handleChangeCategory(id, categoryId) {
    const updated = await updateTransaction(id, { category_id: categoryId });
    setTransactions((prev) => prev.map((t) => (t.id === id ? updated : t)));
  }

  async function handleDelete(id) {
    await deleteTransaction(id);
    setTransactions((prev) => prev.filter((t) => t.id !== id));
  }

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div>
      <h1>Transactions</h1>
      <div className="toolbar">
        <CsvImport onImported={refreshTransactions} />
        <AutoCategorizeButton onDone={refreshTransactions} />
      </div>
      <TransactionForm categories={categories} onCreate={handleCreate} />
      <TransactionList
        transactions={transactions}
        categories={categories}
        onChangeCategory={handleChangeCategory}
        onDelete={handleDelete}
      />
    </div>
  );
}
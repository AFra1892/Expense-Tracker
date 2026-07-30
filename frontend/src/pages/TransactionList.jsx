export default function TransactionList({ transactions, categories, onChangeCategory, onDelete }) {
  if (transactions.length === 0) {
    return <p className="empty-state">No transactions yet — add your first one above.</p>;
  }

  return (
    <table className="transaction-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Description</th>
          <th>Amount</th>
          <th>Category</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {transactions.map((txn) => (
          <tr key={txn.id}>
            <td>{txn.date}</td>
            <td>{txn.description}</td>
            <td className={txn.amount < 0 ? "amount-negative" : ""}>${txn.amount.toFixed(2)}</td>
            <td>
              <select
                value={txn.category?.id || ""}
                onChange={(e) => onChangeCategory(txn.id, e.target.value || null)}
              >
                <option value="">Uncategorized</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
              {txn.category_source === "model" && <span className="badge">AI</span>}
            </td>
            <td>
              <button className="link-button" onClick={() => onDelete(txn.id)}>
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
import apiClient from "./client";

export async function fetchTransactions() {
  const { data } = await apiClient.get("/transactions");
  return data;
}

export async function createTransaction(txn) {
  const { data } = await apiClient.post("/transactions", txn);
  return data;
}

export async function updateTransaction(id, updates) {
  const { data } = await apiClient.put(`/transactions/${id}`, updates);
  return data;
}

export async function deleteTransaction(id) {
  await apiClient.delete(`/transactions/${id}`);
}
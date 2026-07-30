import apiClient from "./client";

export async function fetchCategoryBreakdown() {
  const { data } = await apiClient.get("/reports/by-category");
  return data;
}

export async function fetchMonthlyTotals() {
  const { data } = await apiClient.get("/reports/monthly");
  return data;
}
import apiClient from "./client";

export async function fetchCategories() {
  const { data } = await apiClient.get("/categories");
  return data;
}
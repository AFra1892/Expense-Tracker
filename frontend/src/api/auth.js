import apiClient from "./client";

export async function registerUser(email, password) {
  const { data } = await apiClient.post("/auth/register", { email, password });
  return data;
}

export async function loginUser(email, password) {
  // The backend uses OAuth2PasswordRequestForm, which expects form-urlencoded
  // data with "username" and "password" fields (not JSON).
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);

  const { data } = await apiClient.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data; // { access_token, token_type }
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get("/auth/me");
  return data;
}

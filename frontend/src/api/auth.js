import { api } from "./client.js";

export const authApi = {
  async login(email, password) {
    const data = await api.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (data?.access_token) {
      api.setToken(data.access_token);
    }
    return data;
  },

  async register(email, password, fullName = "") {
    return api.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
        full_name: fullName || null,
      }),
    });
  },

  async getMe() {
    return api.request("/auth/me");
  },

  async completeOnboarding() {
    return api.request("/auth/onboarding/complete", {
      method: "POST",
    });
  },

  logout() {
    api.setToken(null);
  },

  isAuthenticated() {
    return !!api.getToken();
  },
};

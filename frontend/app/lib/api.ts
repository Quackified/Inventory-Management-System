import axios from "axios";
import { clearAuthSession } from "./auth";

const envApiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const baseURL = typeof envApiBaseUrl === "string" && envApiBaseUrl.trim()
  ? envApiBaseUrl.trim()
  : "http://127.0.0.1:20006";

export const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

if (typeof window !== "undefined") {
  const persistedToken = window.localStorage.getItem("inventory_auth_token");
  if (persistedToken) {
    setAuthToken(persistedToken);
  }
}

api.interceptors.request.use((config) => {
  if (typeof window === "undefined") {
    return config;
  }

  const token = window.localStorage.getItem("inventory_auth_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (!axios.isAxiosError(error)) {
      return Promise.reject(error);
    }

    const originalRequest = error.config;
    const status = error.response?.status;
    if (status === 401 && typeof window !== "undefined") {
      clearAuthSession();
      setAuthToken(null);

      const requestUrl = originalRequest?.url ?? "";
      const isLoginRequest = typeof requestUrl === "string" && requestUrl.includes("/api/v1/auth/login");
      if (!isLoginRequest) {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  },
);

export function getApiErrorMessage(error: unknown, fallback = "Something went wrong. Please try again.") {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const payload = error.response?.data as unknown;

    if (typeof payload === "string" && payload.trim()) {
      return payload;
    }

    if (payload && typeof payload === "object") {
      const details = payload as Record<string, unknown>;
      const detail = details.detail;
      const message = details.message;
      const errorText = details.error;

      if (typeof detail === "string" && detail.trim()) return detail;
      if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0] as Record<string, unknown>;
        const msg = typeof first?.msg === "string" ? first.msg.trim() : "";
        const locArray = Array.isArray(first?.loc) ? (first.loc as unknown[]) : [];
        const loc = locArray
          .map((part) => String(part))
          .filter((part) => part !== "body")
          .join(".");

        if (msg && loc) return `${loc}: ${msg}`;
        if (msg) return msg;
      }
      if (typeof message === "string" && message.trim()) return message;
      if (typeof errorText === "string" && errorText.trim()) return errorText;
    }

    if (status === 401) return "Invalid credentials. Please verify your username and password.";
    if (status === 403) return "You do not have permission to perform this action.";
    if (status === 404) return "The requested resource was not found.";
    if (status === 422) return "Please review the input values and try again.";
    if (status && status >= 500) return "Server error. Please try again in a moment.";
  }

  if (error instanceof Error && error.message && !/request failed/i.test(error.message)) {
    return error.message;
  }

  return fallback;
}

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";

import type { ApiEnvelope } from "@/types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const ACCESS_KEY = "ca_access";
const REFRESH_KEY = "ca_refresh";

// ---------------------------------------------------------------------------
// Token storage - localStorage in the browser, no-op on the server
// ---------------------------------------------------------------------------
export const tokenStore = {
  get access(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(ACCESS_KEY);
  },
  get refresh(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(REFRESH_KEY);
  },
  set(access: string, refresh: string) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(ACCESS_KEY, access);
    window.localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
  },
};

// ---------------------------------------------------------------------------
// Axios instance with auth + 401 refresh interceptor
// ---------------------------------------------------------------------------
export const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 20000,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.access;
  if (token) {
    config.headers.set?.("Authorization", `Bearer ${token}`);
  }
  return config;
});

let refreshing: Promise<string | null> | null = null;

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (
      error.response?.status === 401 &&
      tokenStore.refresh &&
      original &&
      !original._retry &&
      !original.url?.includes("/auth/refresh")
    ) {
      original._retry = true;
      try {
        const newAccess = await refreshAccessToken();
        if (newAccess) {
          original.headers.set?.("Authorization", `Bearer ${newAccess}`);
          return api.request(original);
        }
      } catch {
        // fall through
      }
      tokenStore.clear();
      if (typeof window !== "undefined") window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

async function refreshAccessToken(): Promise<string | null> {
  if (refreshing) return refreshing;
  refreshing = (async () => {
    try {
      const r = await axios.post<ApiEnvelope<{ access: string; refresh?: string }>>(
        `${BASE_URL}/auth/refresh/`,
        { refresh: tokenStore.refresh }
      );
      const access = r.data?.data?.access ?? null;
      const refresh = r.data?.data?.refresh ?? tokenStore.refresh ?? "";
      if (access) tokenStore.set(access, refresh ?? "");
      return access;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

// ---------------------------------------------------------------------------
// Convenience request helpers that unwrap the envelope
// ---------------------------------------------------------------------------
export async function apiGet<T>(url: string, params?: object): Promise<T> {
  const r = await api.get<ApiEnvelope<T>>(url, { params });
  if (!r.data.success || r.data.data == null) throw new Error(r.data.message);
  return r.data.data;
}

export async function apiPost<T>(url: string, body?: unknown): Promise<T> {
  const r = await api.post<ApiEnvelope<T>>(url, body);
  if (!r.data.success || r.data.data == null) throw new Error(r.data.message);
  return r.data.data;
}

export async function apiPatch<T>(url: string, body?: unknown): Promise<T> {
  const r = await api.patch<ApiEnvelope<T>>(url, body);
  if (!r.data.success) throw new Error(r.data.message);
  return r.data.data as T;
}

export async function apiDelete(url: string): Promise<void> {
  await api.delete(url);
}

import { create } from "zustand";

import { api, apiPost, tokenStore } from "@/lib/api";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  loading: boolean;
  hydrate: () => Promise<void>;
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
}

interface LoginPayload {
  access: string;
  refresh: string;
  user: User;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,

  /** Try to fetch the current user using stored tokens. */
  async hydrate() {
    if (!tokenStore.access) {
      set({ user: null, loading: false });
      return;
    }
    try {
      const r = await api.get("/auth/me/");
      set({ user: r.data.data as User, loading: false });
    } catch {
      tokenStore.clear();
      set({ user: null, loading: false });
    }
  },

  async login(email, password) {
    const data = await apiPost<LoginPayload>("/auth/login/", { email, password });
    tokenStore.set(data.access, data.refresh);
    set({ user: data.user });
    return data.user;
  },

  async logout() {
    const refresh = tokenStore.refresh;
    try {
      if (refresh) await apiPost("/auth/logout/", { refresh });
    } catch {
      /* ignore */
    }
    tokenStore.clear();
    set({ user: null });
  },
}));

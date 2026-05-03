"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/store/auth-store";
import type { UserRole } from "@/types";

/**
 * Convenience hook used by protected pages.  Hydrates the auth store on
 * mount and redirects to /login if the user is missing or the role doesn't
 * match an optional allowlist.
 */
export function useRequireAuth(allowedRoles?: UserRole[]) {
  const { user, loading, hydrate } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (loading) hydrate();
  }, [loading, hydrate]);

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/login");
      return;
    }
    if (allowedRoles && !allowedRoles.includes(user.role)) {
      router.replace(`/dashboard/${user.role}`);
    }
  }, [loading, user, allowedRoles, router]);

  return { user, loading };
}

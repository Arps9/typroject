"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/store/auth-store";

export default function DashboardRoot() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    if (user) router.replace(`/dashboard/${user.role}`);
  }, [user, router]);

  return <div className="text-slate-500">Routing to your dashboard…</div>;
}

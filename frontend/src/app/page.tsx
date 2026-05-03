"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/store/auth-store";

export default function Home() {
  const { user, loading, hydrate } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (loading) hydrate();
  }, [loading, hydrate]);

  useEffect(() => {
    if (loading) return;
    if (!user) router.replace("/login");
    else router.replace("/dashboard");
  }, [loading, user, router]);

  return (
    <div className="min-h-screen grid place-items-center text-slate-500">
      Loading…
    </div>
  );
}

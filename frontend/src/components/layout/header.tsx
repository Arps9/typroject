"use client";

import { LogOut, User as UserIcon } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/auth-store";

export function Header() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <h2 className="text-sm font-medium text-slate-600">
        {user?.company_name ?? "Compliance Audit Platform"}
      </h2>
      <div className="flex items-center gap-3">
        {user && (
          <div className="flex items-center gap-2 text-sm">
            <div className="w-8 h-8 rounded-full bg-brand-700 text-white grid place-items-center">
              <UserIcon className="w-4 h-4" />
            </div>
            <div className="text-right leading-tight">
              <div className="font-medium text-slate-900">{user.full_name}</div>
              <div className="text-xs text-slate-500 capitalize">{user.role}</div>
            </div>
          </div>
        )}
        <Button variant="outline" size="sm" onClick={handleLogout}>
          <LogOut className="w-4 h-4" />
          Logout
        </Button>
      </div>
    </header>
  );
}

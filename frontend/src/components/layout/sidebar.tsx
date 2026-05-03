"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ShieldCheck,
  ClipboardList,
  FileBarChart,
  Building2,
  Users,
  FileCheck2,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import type { UserRole } from "@/types";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  roles?: UserRole[];
}

const NAV: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/audits", label: "Audits", icon: ShieldCheck },
  { href: "/tasks", label: "Tasks", icon: ClipboardList },
  { href: "/reviews", label: "Reviews", icon: FileCheck2, roles: ["admin", "auditor"] },
  { href: "/reports", label: "Reports", icon: FileBarChart, roles: ["admin", "auditor"] },
  { href: "/departments", label: "Departments", icon: Building2, roles: ["admin"] },
  { href: "/users", label: "Users", icon: Users, roles: ["admin"] },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="hidden md:flex w-64 flex-col bg-slate-900 text-slate-200 min-h-screen">
      <div className="px-6 py-5 border-b border-slate-800">
        <p className="text-xs uppercase tracking-wider text-slate-400">Compliance</p>
        <h1 className="text-lg font-semibold text-white">Audit Manager</h1>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.filter((n) => !n.roles || (user && n.roles.includes(user.role))).map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                active
                  ? "bg-slate-800 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="px-4 py-4 border-t border-slate-800 text-xs text-slate-500">
        v1.0.0 · MVP
      </div>
    </aside>
  );
}

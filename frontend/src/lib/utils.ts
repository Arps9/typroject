import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge tailwind classes safely.  Used by every UI component.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleDateString();
  } catch {
    return value;
  }
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    draft: "bg-slate-100 text-slate-700",
    assigned: "bg-blue-100 text-blue-700",
    in_progress: "bg-yellow-100 text-yellow-800",
    submitted: "bg-indigo-100 text-indigo-700",
    under_review: "bg-purple-100 text-purple-700",
    approved: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
    closed: "bg-slate-200 text-slate-800",
    overdue: "bg-red-100 text-red-700",
    scheduled: "bg-blue-100 text-blue-700",
    active: "bg-green-100 text-green-700",
    reviewing: "bg-purple-100 text-purple-700",
    cancelled: "bg-slate-200 text-slate-700",
  };
  return map[status] ?? "bg-slate-100 text-slate-700";
}

export function riskColor(risk: string): string {
  const map: Record<string, string> = {
    low: "bg-green-100 text-green-700",
    medium: "bg-yellow-100 text-yellow-800",
    high: "bg-orange-100 text-orange-800",
    critical: "bg-red-100 text-red-700",
  };
  return map[risk] ?? "bg-slate-100 text-slate-700";
}

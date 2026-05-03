import { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: number | string;
  hint?: string;
  icon?: LucideIcon;
  accent?: "blue" | "green" | "amber" | "red" | "slate";
}

const ACCENTS = {
  blue: "bg-blue-50 text-blue-700",
  green: "bg-green-50 text-green-700",
  amber: "bg-amber-50 text-amber-700",
  red: "bg-red-50 text-red-700",
  slate: "bg-slate-100 text-slate-700",
};

export function StatCard({ label, value, hint, icon: Icon, accent = "slate" }: StatCardProps) {
  return (
    <Card>
      <CardContent className="p-5 flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
          <p className="text-3xl font-semibold text-slate-900 mt-1">{value}</p>
          {hint && <p className="text-xs text-slate-500 mt-1">{hint}</p>}
        </div>
        {Icon && (
          <div className={cn("rounded-lg p-2", ACCENTS[accent])}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

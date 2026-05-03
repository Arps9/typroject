"use client";

import { useEffect, useState } from "react";
import { ClipboardList, AlertTriangle, Building2, BarChart3 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRequireAuth } from "@/hooks/use-auth";
import { apiGet } from "@/lib/api";
import type { DepartmentDashboard } from "@/types";

const COLORS = ["#1d4ed8", "#0ea5e9", "#22c55e", "#eab308", "#f97316",
                "#ef4444", "#a855f7", "#64748b", "#14b8a6"];

export default function DepartmentDashboardPage() {
  useRequireAuth(["department"]);
  const [data, setData] = useState<DepartmentDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<DepartmentDashboard>("/analytics/dashboard/department/")
      .then(setData)
      .catch((e) => setError(e.message ?? "Failed to load"));
  }, []);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!data) return <p className="text-slate-500">Loading…</p>;

  const s = data.summary;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Department Dashboard</h1>
        <p className="text-sm text-slate-500">Your assigned tasks and department posture.</p>
      </div>

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="My Open Tasks" value={Number(s.my_open_tasks ?? 0)} icon={ClipboardList} accent="blue" />
        <StatCard label="My Overdue" value={Number(s.my_overdue_tasks ?? 0)} icon={AlertTriangle} accent="red" />
        <StatCard label="Department Tasks" value={Number(s.department_total ?? 0)} icon={Building2} accent="slate" />
        <StatCard
          label="Compliance Score"
          value={`${Number(s.department_compliance ?? 0).toFixed(1)}%`}
          icon={BarChart3}
          accent="green"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>My Tasks by Status</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.tasks_by_status}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.tasks_by_status.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

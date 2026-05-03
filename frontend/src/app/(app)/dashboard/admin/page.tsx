"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, ClipboardList, AlertTriangle, BarChart3 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRequireAuth } from "@/hooks/use-auth";
import { apiGet } from "@/lib/api";
import type { AdminDashboard } from "@/types";

const PIE_COLORS = ["#1d4ed8", "#0ea5e9", "#22c55e", "#eab308", "#f97316", "#ef4444",
                    "#a855f7", "#64748b", "#14b8a6"];

export default function AdminDashboardPage() {
  useRequireAuth(["admin"]);
  const [data, setData] = useState<AdminDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<AdminDashboard>("/analytics/dashboard/admin/")
      .then(setData)
      .catch((e) => setError(e.message ?? "Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-500">Loading dashboard…</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (!data) return null;

  const s = data.summary;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Admin Dashboard</h1>
        <p className="text-sm text-slate-500">Company-wide compliance posture.</p>
      </div>

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Audits" value={Number(s.total_audits ?? 0)} icon={ShieldCheck} accent="blue" />
        <StatCard label="Active Audits" value={Number(s.active_audits ?? 0)} icon={BarChart3} accent="green" />
        <StatCard label="Total Tasks" value={Number(s.total_tasks ?? 0)} icon={ClipboardList} accent="slate" />
        <StatCard
          label="Overdue Tasks"
          value={Number(s.overdue_tasks ?? 0)}
          icon={AlertTriangle}
          accent="red"
        />
        <StatCard
          label="Approved Tasks"
          value={Number(s.approved_tasks ?? 0)}
          accent="green"
        />
        <StatCard
          label="Avg. Compliance"
          value={`${(Number(s.average_compliance_score ?? 0)).toFixed(1)}%`}
          accent="blue"
        />
      </div>

      <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Tasks by Status</CardTitle>
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
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Audits by Risk Level</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.audits_by_risk}
                  dataKey="count"
                  nameKey="label"
                  innerRadius={50}
                  outerRadius={90}
                  paddingAngle={2}
                >
                  {data.audits_by_risk.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Legend verticalAlign="bottom" height={28} />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Department Compliance</CardTitle>
        </CardHeader>
        <CardContent className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.department_compliance} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
              <YAxis dataKey="department_name" type="category" tick={{ fontSize: 11 }} width={120} />
              <Tooltip />
              <Bar dataKey="score" fill="#1d4ed8" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

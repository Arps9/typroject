"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, ClipboardCheck, ListChecks, CheckCircle2 } from "lucide-react";
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
import type { AuditorDashboard } from "@/types";

const COLORS = ["#1d4ed8", "#0ea5e9", "#22c55e", "#eab308", "#f97316",
                "#ef4444", "#a855f7", "#64748b", "#14b8a6"];

export default function AuditorDashboardPage() {
  useRequireAuth(["auditor"]);
  const [data, setData] = useState<AuditorDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<AuditorDashboard>("/analytics/dashboard/auditor/")
      .then(setData)
      .catch((e) => setError(e.message ?? "Failed to load"));
  }, []);

  if (error) return <p className="text-red-600">{error}</p>;
  if (!data) return <p className="text-slate-500">Loading…</p>;

  const s = data.summary;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Auditor Dashboard</h1>
        <p className="text-sm text-slate-500">Audits and reviews assigned to you.</p>
      </div>

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="My Audits" value={Number(s.my_audits ?? 0)} icon={ShieldCheck} accent="blue" />
        <StatCard label="Active" value={Number(s.active_audits ?? 0)} icon={ClipboardCheck} accent="green" />
        <StatCard label="Review Queue" value={Number(s.review_queue ?? 0)} icon={ListChecks} accent="amber" />
        <StatCard label="Approved" value={Number(s.approved_today ?? 0)} icon={CheckCircle2} accent="green" />
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

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { useRequireAuth } from "@/hooks/use-auth";
import { apiGet } from "@/lib/api";
import { formatDate, riskColor, statusColor } from "@/lib/utils";
import type { ComplianceTask, Paginated } from "@/types";

const STATUS_FILTERS = [
  "all", "draft", "assigned", "in_progress", "submitted",
  "under_review", "approved", "rejected", "overdue", "closed",
] as const;

export default function TasksPage() {
  useRequireAuth();
  const [tasks, setTasks] = useState<ComplianceTask[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<typeof STATUS_FILTERS[number]>("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = setTimeout(async () => {
      try {
        const params: Record<string, string> = { search };
        if (statusFilter !== "all") params.status = statusFilter;
        const data = await apiGet<Paginated<ComplianceTask>>("/tasks/", params);
        setTasks(data.results);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load");
      }
    }, 250);
    return () => clearTimeout(t);
  }, [search, statusFilter]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Tasks</h1>
          <p className="text-sm text-slate-500">Compliance tasks visible to you.</p>
        </div>
        <Input
          placeholder="Search tasks…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {STATUS_FILTERS.map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={
              "px-3 py-1.5 rounded-full text-xs font-medium border transition-colors " +
              (statusFilter === s
                ? "bg-brand-700 text-white border-brand-700"
                : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50")
            }
          >
            {s.replace("_", " ")}
          </button>
        ))}
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      <Card>
        <CardHeader>
          <CardTitle>{tasks.length} task{tasks.length === 1 ? "" : "s"}</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <THead>
              <TR>
                <TH>Title</TH>
                <TH>Status</TH>
                <TH>Risk</TH>
                <TH>Audit</TH>
                <TH>Department</TH>
                <TH>Assignee</TH>
                <TH>Due</TH>
              </TR>
            </THead>
            <TBody>
              {tasks.length === 0 && (
                <TR>
                  <TD colSpan={7} className="text-center text-slate-500 py-8">
                    No tasks found.
                  </TD>
                </TR>
              )}
              {tasks.map((t) => (
                <TR key={t.id}>
                  <TD>
                    <Link href={`/tasks/${t.id}`} className="font-medium text-brand-700 hover:underline">
                      {t.title}
                    </Link>
                  </TD>
                  <TD>
                    <Badge className={statusColor(t.status)}>
                      {t.is_overdue ? "overdue" : t.status}
                    </Badge>
                  </TD>
                  <TD><Badge className={riskColor(t.risk_level)}>{t.risk_level}</Badge></TD>
                  <TD>
                    <Link href={`/audits/${t.audit}`} className="hover:underline">
                      {t.audit_title ?? "—"}
                    </Link>
                  </TD>
                  <TD>{t.department_name ?? "—"}</TD>
                  <TD>{t.assigned_to_detail?.full_name ?? "—"}</TD>
                  <TD>{formatDate(t.due_date ?? null)}</TD>
                </TR>
              ))}
            </TBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

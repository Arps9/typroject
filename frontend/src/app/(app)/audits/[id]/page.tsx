"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { FileDown } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { useRequireAuth } from "@/hooks/use-auth";
import { apiGet, apiPost } from "@/lib/api";
import { formatDate, riskColor, statusColor } from "@/lib/utils";
import type { Audit, ComplianceTask, Paginated } from "@/types";

export default function AuditDetailPage() {
  const { user } = useRequireAuth();
  const params = useParams<{ id: string }>();
  const id = params?.id;

  const [audit, setAudit] = useState<Audit | null>(null);
  const [tasks, setTasks] = useState<ComplianceTask[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    if (!id) return;
    try {
      const a = await apiGet<Audit>(`/audits/${id}/`);
      setAudit(a);
      const t = await apiGet<Paginated<ComplianceTask>>("/tasks/", { audit: id });
      setTasks(t.results);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  }

  useEffect(() => { load(); }, [id]);

  async function transition(target: string) {
    if (!audit) return;
    setBusy(true);
    try {
      await apiPost(`/audits/${audit.id}/transition/`, { status: target });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Transition failed");
    } finally {
      setBusy(false);
    }
  }

  if (error) return <p className="text-red-600">{error}</p>;
  if (!audit) return <p className="text-slate-500">Loading…</p>;

  const canActOnAudit = user && (user.role === "admin" || user.role === "auditor");
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold">{audit.title}</h1>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <Badge className={statusColor(audit.status)}>{audit.status}</Badge>
            <Badge className={riskColor(audit.risk_level)}>{audit.risk_level} risk</Badge>
            <span className="text-sm text-slate-500">{audit.audit_type}</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <a
            href={`${apiBase}/reports/audit/${audit.id}/pdf/`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 h-8 px-3 rounded-md text-sm border border-slate-300 bg-white hover:bg-slate-50"
          >
            <FileDown className="w-4 h-4" />
            PDF
          </a>
          <a
            href={`${apiBase}/reports/audit/${audit.id}/tasks.csv`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 h-8 px-3 rounded-md text-sm border border-slate-300 bg-white hover:bg-slate-50"
          >
            <FileDown className="w-4 h-4" />
            CSV
          </a>
        </div>
      </div>

      <div className="grid gap-6 grid-cols-1 lg:grid-cols-3">
        <Card>
          <CardHeader><CardTitle>Details</CardTitle></CardHeader>
          <CardContent className="text-sm space-y-2">
            <Row label="Lead auditor" value={audit.lead_auditor_detail?.full_name ?? "—"} />
            <Row label="Scheduled" value={`${formatDate(audit.scheduled_start)} → ${formatDate(audit.scheduled_end)}`} />
            <Row
              label="Actual"
              value={audit.actual_start
                ? `${formatDate(audit.actual_start)} → ${formatDate(audit.actual_end)}`
                : "—"}
            />
            <Row label="Compliance score" value={audit.compliance_score ? `${audit.compliance_score}%` : "—"} />
            <Row label="Tasks" value={String(audit.task_count ?? tasks.length)} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Description</CardTitle></CardHeader>
          <CardContent className="text-sm whitespace-pre-line text-slate-700">
            {audit.description || "No description."}
          </CardContent>
        </Card>
      </div>

      {canActOnAudit && (
        <Card>
          <CardHeader><CardTitle>Lifecycle</CardTitle></CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Button size="sm" disabled={busy || audit.status !== "scheduled"} onClick={() => transition("active")}>
              Start (Active)
            </Button>
            <Button size="sm" variant="outline" disabled={busy || audit.status !== "active"} onClick={() => transition("reviewing")}>
              Move to Reviewing
            </Button>
            <Button size="sm" variant="outline" disabled={busy || audit.status !== "reviewing"} onClick={() => transition("closed")}>
              Close
            </Button>
            <Button size="sm" variant="destructive" disabled={busy || audit.status === "closed" || audit.status === "cancelled"} onClick={() => transition("cancelled")}>
              Cancel
            </Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle>Tasks ({tasks.length})</CardTitle></CardHeader>
        <CardContent className="p-0">
          <Table>
            <THead>
              <TR>
                <TH>Title</TH>
                <TH>Status</TH>
                <TH>Type</TH>
                <TH>Department</TH>
                <TH>Assignee</TH>
                <TH>Due</TH>
              </TR>
            </THead>
            <TBody>
              {tasks.map((t) => (
                <TR key={t.id}>
                  <TD>
                    <Link href={`/tasks/${t.id}`} className="font-medium text-brand-700 hover:underline">
                      {t.title}
                    </Link>
                  </TD>
                  <TD><Badge className={statusColor(t.status)}>{t.status}</Badge></TD>
                  <TD>{t.task_type}</TD>
                  <TD>{t.department_name ?? "—"}</TD>
                  <TD>{t.assigned_to_detail?.full_name ?? "—"}</TD>
                  <TD>{formatDate(t.due_date ?? null)}</TD>
                </TR>
              ))}
              {tasks.length === 0 && (
                <TR>
                  <TD colSpan={6} className="text-center text-slate-500 py-6">No tasks yet.</TD>
                </TR>
              )}
            </TBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-slate-500">{label}</span>
      <span className="text-slate-900 font-medium text-right">{value}</span>
    </div>
  );
}

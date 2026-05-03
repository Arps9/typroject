"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Upload, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRequireAuth } from "@/hooks/use-auth";
import { api, apiGet, apiPost } from "@/lib/api";
import { formatDate, riskColor, statusColor } from "@/lib/utils";
import type { ComplianceTask } from "@/types";

interface Evidence {
  id: string;
  original_filename: string;
  size_bytes: number;
  file_url: string;
  created_at: string;
}

export default function TaskDetailPage() {
  const { user } = useRequireAuth();
  const params = useParams<{ id: string }>();
  const id = params?.id;
  const fileInput = useRef<HTMLInputElement>(null);

  const [task, setTask] = useState<ComplianceTask | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [aiResult, setAiResult] = useState<{ result: string; confidence: string; notes: string } | null>(null);

  async function load() {
    if (!id) return;
    try {
      const t = await apiGet<ComplianceTask>(`/tasks/${id}/`);
      setTask(t);
      const ev = await apiGet<{ results: Evidence[] }>(`/evidence/`, { task: id });
      setEvidence(ev.results ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  }
  useEffect(() => { load(); }, [id]);

  async function transition(target: string) {
    if (!task) return;
    setBusy(true);
    try {
      await apiPost(`/tasks/${task.id}/transition/`, { status: target });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Transition failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleUpload(file: File) {
    if (!task) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("task", task.id);
      await api.post("/evidence/", fd, { headers: { "Content-Type": "multipart/form-data" } });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function runAI(evidenceId: string) {
    setAiResult(null);
    try {
      const r = await apiPost<{ result: string; confidence: string; notes: string }>(
        "/ai/results/verify/",
        { evidence_id: evidenceId }
      );
      setAiResult(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : "AI verification failed");
    }
  }

  if (error) return <p className="text-red-600">{error}</p>;
  if (!task) return <p className="text-slate-500">Loading…</p>;

  const canReview = user && (user.role === "admin" || user.role === "auditor");
  const canSubmit = user && (user.role === "department" && user.id === task.assigned_to);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{task.title}</h1>
        <div className="flex flex-wrap items-center gap-2 mt-2">
          <Badge className={statusColor(task.status)}>{task.status}</Badge>
          <Badge className={riskColor(task.risk_level)}>{task.risk_level} risk</Badge>
          <span className="text-sm text-slate-500">{task.task_type}</span>
          <span className="text-sm text-slate-500">· priority {task.priority}</span>
        </div>
      </div>

      <div className="grid gap-6 grid-cols-1 lg:grid-cols-3">
        <Card>
          <CardHeader><CardTitle>Details</CardTitle></CardHeader>
          <CardContent className="text-sm space-y-2">
            <Row label="Audit" value={
              <Link href={`/audits/${task.audit}`} className="text-brand-700 hover:underline">
                {task.audit_title ?? task.audit}
              </Link>
            } />
            <Row label="Department" value={task.department_name ?? "—"} />
            <Row label="Assignee" value={task.assigned_to_detail?.full_name ?? "—"} />
            <Row label="Due" value={formatDate(task.due_date ?? null)} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Description</CardTitle></CardHeader>
          <CardContent className="text-sm whitespace-pre-line text-slate-700">
            {task.description || "No description provided."}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Evidence</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div
            className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center cursor-pointer hover:border-brand-500 transition-colors"
            onClick={() => fileInput.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              const f = e.dataTransfer.files?.[0];
              if (f) handleUpload(f);
            }}
          >
            <Upload className="w-6 h-6 mx-auto text-slate-400" />
            <p className="text-sm text-slate-600 mt-2">
              {uploading ? "Uploading…" : "Drop a file here or click to upload"}
            </p>
            <p className="text-xs text-slate-400 mt-1">PDF, DOCX, XLSX, CSV, TXT, images, ZIP — up to 50MB</p>
            <input
              ref={fileInput}
              type="file"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleUpload(f);
              }}
            />
          </div>

          {evidence.length > 0 && (
            <ul className="divide-y divide-slate-100">
              {evidence.map((ev) => (
                <li key={ev.id} className="py-2 flex items-center justify-between gap-4">
                  <div className="text-sm">
                    <a className="text-brand-700 hover:underline" href={ev.file_url} target="_blank" rel="noreferrer">
                      {ev.original_filename}
                    </a>
                    <p className="text-xs text-slate-500">
                      {(ev.size_bytes / 1024).toFixed(1)} KB · {formatDate(ev.created_at)}
                    </p>
                  </div>
                  {canReview && (
                    <Button size="sm" variant="outline" onClick={() => runAI(ev.id)}>
                      <Sparkles className="w-4 h-4" />
                      AI verify
                    </Button>
                  )}
                </li>
              ))}
            </ul>
          )}

          {aiResult && (
            <div className="rounded-md border border-brand-200 bg-brand-50 p-3 text-sm">
              <p className="font-medium text-brand-900">AI suggestion (auditor confirms)</p>
              <p className="mt-1">
                Result: <strong>{aiResult.result}</strong>
                {" · "}Confidence: <strong>{aiResult.confidence}%</strong>
              </p>
              <p className="text-slate-700 mt-1">{aiResult.notes}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Workflow</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {canSubmit && task.status === "assigned" && (
            <Button size="sm" disabled={busy} onClick={() => transition("in_progress")}>
              Start working
            </Button>
          )}
          {canSubmit && task.status === "in_progress" && (
            <Button size="sm" disabled={busy} onClick={() => transition("submitted")}>
              Submit for review
            </Button>
          )}
          {canReview && task.status === "submitted" && (
            <Button size="sm" disabled={busy} onClick={() => transition("under_review")}>
              Take for review
            </Button>
          )}
          {canReview && task.status === "under_review" && (
            <>
              <Button size="sm" disabled={busy} onClick={() => transition("approved")}>
                Approve
              </Button>
              <Button size="sm" variant="destructive" disabled={busy} onClick={() => transition("rejected")}>
                Reject
              </Button>
            </>
          )}
          {canReview && task.status === "approved" && (
            <Button size="sm" variant="outline" disabled={busy} onClick={() => transition("closed")}>
              Close
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-slate-500">{label}</span>
      <span className="text-slate-900 font-medium text-right">{value}</span>
    </div>
  );
}

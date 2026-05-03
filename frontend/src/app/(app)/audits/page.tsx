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
import type { Audit, Paginated } from "@/types";

export default function AuditsPage() {
  useRequireAuth();

  const [audits, setAudits] = useState<Audit[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = setTimeout(async () => {
      try {
        const data = await apiGet<Paginated<Audit>>("/audits/", { search });
        setAudits(data.results);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load");
      }
    }, 250);
    return () => clearTimeout(t);
  }, [search]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Audits</h1>
          <p className="text-sm text-slate-500">All audits visible to you.</p>
        </div>
        <Input
          placeholder="Search audits…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      <Card>
        <CardHeader>
          <CardTitle>{audits.length} audit{audits.length === 1 ? "" : "s"}</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <THead>
              <TR>
                <TH>Title</TH>
                <TH>Status</TH>
                <TH>Risk</TH>
                <TH>Lead Auditor</TH>
                <TH>Period</TH>
                <TH>Tasks</TH>
                <TH>Score</TH>
              </TR>
            </THead>
            <TBody>
              {audits.length === 0 && (
                <TR>
                  <TD colSpan={7} className="text-center text-slate-500 py-8">
                    No audits found.
                  </TD>
                </TR>
              )}
              {audits.map((a) => (
                <TR key={a.id} className="cursor-pointer">
                  <TD>
                    <Link href={`/audits/${a.id}`} className="font-medium text-brand-700 hover:underline">
                      {a.title}
                    </Link>
                  </TD>
                  <TD>
                    <Badge className={statusColor(a.status)}>{a.status}</Badge>
                  </TD>
                  <TD>
                    <Badge className={riskColor(a.risk_level)}>{a.risk_level}</Badge>
                  </TD>
                  <TD>{a.lead_auditor_detail?.full_name ?? "—"}</TD>
                  <TD>{formatDate(a.scheduled_start)} → {formatDate(a.scheduled_end)}</TD>
                  <TD>{a.task_count ?? 0}</TD>
                  <TD>{a.compliance_score ? `${a.compliance_score}%` : "—"}</TD>
                </TR>
              ))}
            </TBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

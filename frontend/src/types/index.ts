// Shared TypeScript types mirroring the backend serializers.

export type UUID = string;

export type UserRole = "admin" | "auditor" | "department";

export interface User {
  id: UUID;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  company?: UUID | null;
  company_name?: string | null;
  department?: UUID | null;
  department_name?: string | null;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  message: string;
  errors: unknown;
}

export interface Paginated<T> {
  results: T[];
  pagination: {
    count: number;
    page: number;
    page_size: number;
    total_pages: number;
    next: string | null;
    previous: string | null;
  };
}

export type AuditStatus =
  | "scheduled"
  | "active"
  | "reviewing"
  | "closed"
  | "cancelled";

export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface Audit {
  id: UUID;
  title: string;
  description?: string;
  audit_type: string;
  risk_level: RiskLevel;
  status: AuditStatus;
  scheduled_start: string;
  scheduled_end: string;
  actual_start?: string | null;
  actual_end?: string | null;
  lead_auditor: UUID;
  lead_auditor_detail?: { id: UUID; email: string; full_name: string; role: UserRole };
  department_count?: number;
  task_count?: number;
  compliance_score?: string | null;
  created_at?: string;
  updated_at?: string;
}

export type TaskStatus =
  | "draft"
  | "assigned"
  | "in_progress"
  | "submitted"
  | "under_review"
  | "approved"
  | "rejected"
  | "closed"
  | "overdue";

export interface ComplianceTask {
  id: UUID;
  title: string;
  task_type: string;
  priority: string;
  risk_level: RiskLevel;
  audit: UUID;
  audit_title?: string;
  department: UUID;
  department_name?: string;
  assigned_to?: UUID | null;
  assigned_to_detail?: { id: UUID; email: string; full_name: string; role: UserRole } | null;
  due_date?: string | null;
  status: TaskStatus;
  is_overdue?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface DashboardSummary {
  [key: string]: number;
}

export interface DashboardStatusBreakdown {
  label: string;
  value: string;
  count: number;
}

export interface AdminDashboard {
  summary: DashboardSummary;
  tasks_by_status: DashboardStatusBreakdown[];
  audits_by_risk: DashboardStatusBreakdown[];
  department_compliance: { department_id: UUID; department_name: string; score: number }[];
}

export interface AuditorDashboard {
  summary: DashboardSummary;
  tasks_by_status: DashboardStatusBreakdown[];
}

export interface DepartmentDashboard {
  summary: DashboardSummary;
  tasks_by_status: DashboardStatusBreakdown[];
}

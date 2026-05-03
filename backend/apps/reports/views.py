from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.audits.models import Audit
from apps.core.responses import envelope

from .services import audit_summary_pdf, audit_tasks_csv


class AuditPDFReportView(APIView):
    """GET /api/v1/reports/audit/<id>/pdf  -> PDF download."""

    permission_classes = [IsAuthenticated]

    def get(self, request, audit_id):
        try:
            audit = Audit.objects.get(pk=audit_id)
        except Audit.DoesNotExist:
            return envelope(None, message="Audit not found", status=404)

        pdf = audit_summary_pdf(audit)
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="audit-{audit.id}.pdf"'
        return resp


class AuditTasksCSVReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, audit_id):
        try:
            audit = Audit.objects.get(pk=audit_id)
        except Audit.DoesNotExist:
            return envelope(None, message="Audit not found", status=404)

        csv_bytes = audit_tasks_csv(audit)
        resp = HttpResponse(csv_bytes, content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="audit-{audit.id}-tasks.csv"'
        return resp

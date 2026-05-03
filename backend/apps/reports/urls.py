from django.urls import path

from .views import AuditPDFReportView, AuditTasksCSVReportView

urlpatterns = [
    path("audit/<uuid:audit_id>/pdf/", AuditPDFReportView.as_view(), name="audit-pdf"),
    path("audit/<uuid:audit_id>/tasks.csv", AuditTasksCSVReportView.as_view(), name="audit-tasks-csv"),
]

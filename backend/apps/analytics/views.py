from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsAuditor, IsDepartmentUser
from apps.core.responses import envelope

from .services import admin_dashboard, auditor_dashboard, department_dashboard


class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        company_id = request.user.company_id
        return envelope(admin_dashboard(company_id), message="Admin dashboard")


class AuditorDashboardView(APIView):
    permission_classes = [IsAuditor]

    def get(self, request):
        return envelope(auditor_dashboard(request.user), message="Auditor dashboard")


class DepartmentDashboardView(APIView):
    permission_classes = [IsDepartmentUser]

    def get(self, request):
        return envelope(department_dashboard(request.user), message="Department dashboard")


class MyDashboardView(APIView):
    """Auto-routes to the correct dashboard based on the user's role."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        if u.is_admin:
            data = admin_dashboard(u.company_id)
        elif u.is_auditor:
            data = auditor_dashboard(u)
        elif u.is_department_user:
            data = department_dashboard(u)
        else:
            data = {}
        return envelope({"role": u.role, "dashboard": data}, message="Dashboard")

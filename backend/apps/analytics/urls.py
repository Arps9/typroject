from django.urls import path

from .views import (
    AdminDashboardView,
    AuditorDashboardView,
    DepartmentDashboardView,
    MyDashboardView,
)

urlpatterns = [
    path("dashboard/admin/", AdminDashboardView.as_view(), name="dashboard-admin"),
    path("dashboard/auditor/", AuditorDashboardView.as_view(), name="dashboard-auditor"),
    path("dashboard/department/", DepartmentDashboardView.as_view(), name="dashboard-department"),
    path("dashboard/me/", MyDashboardView.as_view(), name="dashboard-me"),
]

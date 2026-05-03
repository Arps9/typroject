"""WSGI entry-point for the Compliance Audit project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "compliance_audit.settings.production"
)

application = get_wsgi_application()

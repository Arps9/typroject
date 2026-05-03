"""Compliance Audit project package.

Importing the celery app on package init ensures that the @shared_task
decorator works in any installed app without explicit registration.
"""
from .celery import app as celery_app

__all__ = ("celery_app",)

"""Production settings.

Hardened defaults:
  - DEBUG off
  - Strict CORS
  - HSTS / SSL redirect
  - Stricter throttles
"""
from __future__ import annotations

from .base import *  # noqa: F401,F403

DEBUG = False

# --- HTTPS / Security ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# Tighter throttles
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "user": "500/hour",
    "anon": "30/hour",
}

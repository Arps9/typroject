"""Development settings.

Optimised for local debugging:
  - DEBUG on
  - Permissive CORS
  - Console email backend
  - Browsable API renderer
"""
from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import REST_FRAMEWORK

DEBUG = True

# Show browsable API in dev
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
)

# Allow any localhost CORS origin in dev
CORS_ALLOW_ALL_ORIGINS = True

# Quieter test runs
LOGGING_CONFIG = None  # noqa

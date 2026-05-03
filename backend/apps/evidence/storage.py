"""Storage abstraction.

Currently delegates to Django's default storage (FileSystemStorage in dev,
S3Storage in prod when ``FILE_STORAGE_BACKEND=s3``).  Provides a single API
surface so views/services don't depend on the backend.
"""
from __future__ import annotations

import hashlib
from typing import IO

from django.core.files.storage import default_storage


def save_file(path: str, fp: IO[bytes]) -> str:
    """Save ``fp`` to ``path`` via the default storage; return saved path."""
    return default_storage.save(path, fp)


def delete_file(path: str) -> None:
    if default_storage.exists(path):
        default_storage.delete(path)


def compute_sha256(fp: IO[bytes]) -> str:
    """Compute SHA-256 of a seekable file-like object (rewinds before+after)."""
    fp.seek(0)
    h = hashlib.sha256()
    for chunk in iter(lambda: fp.read(8192), b""):
        h.update(chunk)
    fp.seek(0)
    return h.hexdigest()

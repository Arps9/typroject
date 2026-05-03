"""Document extractors used by the AI engine.

Lightweight wrappers so the rest of the codebase doesn't depend on the
underlying libraries.  Each function returns a string of extracted text;
errors return an empty string and log.

Phase-10 will expand these with structured field extraction and a rule
evaluator.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text(path: str | Path) -> str:
    p = Path(path)
    ext = p.suffix.lower()
    try:
        if ext == ".pdf":
            return _extract_pdf(p)
        if ext in {".docx"}:
            return _extract_docx(p)
        if ext in {".xlsx", ".xls"}:
            return _extract_xlsx(p)
        if ext in {".png", ".jpg", ".jpeg"}:
            return _extract_image_ocr(p)
        if ext in {".txt", ".csv"}:
            return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        logger.exception("Extraction failed for %s", p)
    return ""


def _extract_pdf(path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join((page.extract_text() or "") for page in pdf.pages)
    except ImportError:  # pragma: no cover
        return ""


def _extract_docx(path: Path) -> str:
    try:
        import docx
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:  # pragma: no cover
        return ""


def _extract_xlsx(path: Path) -> str:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        out: list[str] = []
        for ws in wb.worksheets:
            out.append(f"### {ws.title}")
            for row in ws.iter_rows(values_only=True):
                out.append("\t".join("" if c is None else str(c) for c in row))
        return "\n".join(out)
    except ImportError:  # pragma: no cover
        return ""


def _extract_image_ocr(path: Path) -> str:
    try:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(path))
    except ImportError:  # pragma: no cover
        return ""
    except Exception:
        logger.exception("Tesseract failed on %s", path)
        return ""

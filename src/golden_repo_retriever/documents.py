from __future__ import annotations

from pathlib import Path

import fitz


TEXT_SUFFIXES = {".txt", ".md"}
PDF_SUFFIXES = {".pdf"}


def parse_report_file(file_path: str) -> tuple[str, str]:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        return path.read_text(encoding="utf-8"), str(path)
    if suffix in PDF_SUFFIXES:
        return _parse_pdf_bytes(path.read_bytes()), str(path)
    raise ValueError(f"Unsupported report file type: {suffix or '<none>'}")


def parse_report_upload(filename: str, content: bytes) -> tuple[str, str]:
    suffix = Path(filename).suffix.lower()
    if suffix in TEXT_SUFFIXES:
        return content.decode("utf-8"), filename
    if suffix in PDF_SUFFIXES:
        return _parse_pdf_bytes(content), filename
    raise ValueError(f"Unsupported report file type: {suffix or '<none>'}")


def _parse_pdf_bytes(content: bytes) -> str:
    with fitz.open(stream=content, filetype="pdf") as document:
        return "\n".join(page.get_text("text") for page in document).strip()

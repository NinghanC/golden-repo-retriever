from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    query: str = Field(..., description="Finance analysis query.")
    report_text: str | None = Field(default=None, description="Optional plain-text report content.")
    export_path: str | None = Field(default=None, description="Optional JSON output path.")


class AnalyzeResponse(BaseModel):
    query: str
    companies: list[str]
    metrics: dict[str, dict[str, float | str]]
    summary: str
    audit_log: list[dict[str, str]]
    checkpoint_count: int
    report_source: str | None = None
    report_text: str | None = None
    export_path: str | None = None


class HealthResponse(BaseModel):
    status: str


class ConfigResponse(BaseModel):
    app_name: str
    version: str
    workflow: list[str]
    features: dict[str, Any]

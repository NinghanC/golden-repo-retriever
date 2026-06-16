from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    query: str = Field(..., description="Finance analysis query.")
    report_text: str | None = Field(default=None, description="Optional plain-text report content.")
    report_id: int | None = Field(default=None, description="Optional saved report id.")
    export_path: str | None = Field(default=None, description="Optional JSON output path.")
    llm_provider: str | None = Field(default=None, description="Optional provider: local, openai, mistral, or custom.")


class AnalyzeResponse(BaseModel):
    analysis_id: int | None = None
    created_at: str | None = None
    query: str
    companies: list[str]
    extracted_facts: dict[str, dict[str, float | str]] = Field(default_factory=dict)
    evidence: dict[str, list[dict[str, float | str]]] = Field(default_factory=dict)
    metrics: dict[str, dict[str, float | str]]
    market_data: dict[str, dict[str, float | str]] = Field(default_factory=dict)
    summary: str
    llm_provider: str
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


class AnalysisHistoryItem(BaseModel):
    id: int
    created_at: str
    query: str
    companies: str
    summary: str


class JobRequest(BaseModel):
    query: str = Field(..., description="Finance analysis query.")
    report_text: str | None = Field(default=None, description="Optional plain-text report content.")
    report_id: int | None = Field(default=None, description="Optional saved report id.")
    llm_provider: str | None = Field(default=None, description="Optional provider: local, openai, mistral, or custom.")


class JobResponse(BaseModel):
    id: int
    status: str
    query: str
    created_at: str
    updated_at: str
    error: str | None = None
    analysis_id: int | None = None
    report_id: int | None = None
    report_text: str | None = None
    llm_provider: str | None = None


class ReportResponse(BaseModel):
    id: int
    filename: str
    source: str
    content_type: str | None = None
    text: str | None = None
    created_at: str


class ReportListItem(BaseModel):
    id: int
    filename: str
    source: str
    content_type: str | None = None
    created_at: str


class KnowledgeFact(BaseModel):
    id: int
    company: str
    field: str
    value: str
    source: str
    snippet: str | None = None
    analysis_id: int | None = None
    created_at: str

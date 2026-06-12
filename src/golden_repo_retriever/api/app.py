from __future__ import annotations

from fastapi import FastAPI

from ..reporting import export_result
from ..workflow import run_analysis
from .schemas import AnalyzeRequest, AnalyzeResponse, ConfigResponse, HealthResponse


def create_app() -> FastAPI:
    app = FastAPI(
        title="Golden Repo Retriever",
        version="0.1.0",
        description="Local finance-report workflow API for company metrics and summaries.",
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/api/v1/config", response_model=ConfigResponse)
    def config() -> ConfigResponse:
        return ConfigResponse(
            app_name="Golden Repo Retriever",
            version="0.1.0",
            workflow=["query", "report_text", "state", "companies", "metrics", "summary", "audit_log"],
            features={
                "local_text_reports": True,
                "json_export": True,
                "pdf_parsing": False,
            },
        )

    @app.post("/api/v1/analyze", response_model=AnalyzeResponse)
    def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
        result = run_analysis(payload.query, report_text=payload.report_text)
        if payload.export_path:
            result["export_path"] = export_result(result, payload.export_path)
        return AnalyzeResponse(**result)

    return app


app = create_app()

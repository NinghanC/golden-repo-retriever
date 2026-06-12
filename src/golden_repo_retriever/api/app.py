from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from ..documents import parse_report_upload
from ..llm import LLMSettings
from ..reporting import export_result
from ..workflow import run_analysis
from .schemas import AnalyzeRequest, AnalyzeResponse, ConfigResponse, HealthResponse


def create_app() -> FastAPI:
    app = FastAPI(
        title="Golden Repo Retriever",
        version="0.1.0",
        description="Local finance-report workflow API for company metrics and summaries.",
    )
    static_dir = Path(__file__).resolve().parents[3] / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse(url="/static/index.html")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/api/v1/config", response_model=ConfigResponse)
    def config() -> ConfigResponse:
        llm_settings = LLMSettings.from_env()
        return ConfigResponse(
            app_name="Golden Repo Retriever",
            version="0.1.0",
            workflow=["query", "report_text", "state", "companies", "metrics", "summary", "audit_log"],
            features={
                "local_text_reports": True,
                "upload_reports": True,
                "json_export": True,
                "pdf_parsing": True,
                "llm_provider": llm_settings.provider,
                "llm_enabled": bool(llm_settings.api_key),
            },
        )

    @app.post("/api/v1/analyze", response_model=AnalyzeResponse)
    def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
        result = run_analysis(payload.query, report_text=payload.report_text, llm_provider=payload.llm_provider)
        if payload.export_path:
            result["export_path"] = export_result(result, payload.export_path)
        return AnalyzeResponse(**result)

    @app.post("/api/v1/analyze-upload", response_model=AnalyzeResponse)
    async def analyze_upload(
        query: str = Form(...),
        export_path: str | None = Form(default=None),
        llm_provider: str | None = Form(default=None),
        file: UploadFile = File(...),
    ) -> AnalyzeResponse:
        try:
            report_text, source = parse_report_upload(file.filename or "report.txt", await file.read())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        result = run_analysis(query, report_text=report_text, llm_provider=llm_provider)
        result["report_source"] = source
        if export_path:
            result["export_path"] = export_result(result, export_path)
        return AnalyzeResponse(**result)

    return app


app = create_app()

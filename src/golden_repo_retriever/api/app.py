from __future__ import annotations

from threading import Thread
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from ..documents import parse_report_upload
from ..llm import LLMSettings
from ..reporting import export_result
from ..storage import AnalysisStore, DEFAULT_DATABASE_PATH
from ..workflow import run_analysis
from .schemas import (
    AnalysisHistoryItem,
    AnalyzeRequest,
    AnalyzeResponse,
    ConfigResponse,
    HealthResponse,
    JobRequest,
    JobResponse,
)


def create_app(database_path: str | Path = DEFAULT_DATABASE_PATH) -> FastAPI:
    app = FastAPI(
        title="Golden Repo Retriever",
        version="0.1.0",
        description="Local finance-report workflow API for company metrics and summaries.",
    )
    store: AnalysisStore | None = None
    static_dir = Path(__file__).resolve().parents[3] / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    def get_store() -> AnalysisStore:
        nonlocal store
        if store is None:
            store = AnalysisStore(database_path)
        return store

    def run_job(job_id: int) -> None:
        active_store = get_store()
        job = active_store.get_job(job_id)
        if job is None:
            return
        active_store.start_job(job_id)
        try:
            result = run_analysis(
                job["query"],
                report_text=job.get("report_text"),
                llm_provider=job.get("llm_provider"),
            )
            analysis_id = active_store.save(result)
            active_store.complete_job(job_id, analysis_id)
        except Exception as exc:
            active_store.fail_job(job_id, str(exc))

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
                "history": True,
                "background_jobs": True,
                "llm_provider": llm_settings.provider,
                "llm_enabled": bool(llm_settings.api_key),
            },
        )

    @app.post("/api/v1/analyze", response_model=AnalyzeResponse)
    def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
        result = run_analysis(payload.query, report_text=payload.report_text, llm_provider=payload.llm_provider)
        if payload.export_path:
            result["export_path"] = export_result(result, payload.export_path)
        result["analysis_id"] = get_store().save(result)
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
        result["analysis_id"] = get_store().save(result)
        return AnalyzeResponse(**result)

    @app.get("/api/v1/analyses", response_model=list[AnalysisHistoryItem])
    def list_analyses(limit: int = 20) -> list[AnalysisHistoryItem]:
        safe_limit = max(1, min(limit, 100))
        return [AnalysisHistoryItem(**item) for item in get_store().list(limit=safe_limit)]

    @app.get("/api/v1/analyses/{analysis_id}", response_model=AnalyzeResponse)
    def get_analysis(analysis_id: int) -> AnalyzeResponse:
        result = get_store().get(analysis_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Analysis not found.")
        return AnalyzeResponse(**result)

    @app.post("/api/v1/jobs", response_model=JobResponse, status_code=202)
    def create_job(payload: JobRequest) -> JobResponse:
        active_store = get_store()
        job_id = active_store.create_job(
            query=payload.query,
            report_text=payload.report_text,
            llm_provider=payload.llm_provider,
        )
        Thread(target=run_job, args=(job_id,), daemon=True).start()
        job = active_store.get_job(job_id)
        assert job is not None
        return JobResponse(**job)

    @app.get("/api/v1/jobs", response_model=list[JobResponse])
    def list_jobs(limit: int = 20) -> list[JobResponse]:
        safe_limit = max(1, min(limit, 100))
        return [JobResponse(**item) for item in get_store().list_jobs(limit=safe_limit)]

    @app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
    def get_job(job_id: int) -> JobResponse:
        job = get_store().get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found.")
        return JobResponse(**job)

    return app


app = create_app()

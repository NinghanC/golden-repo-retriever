from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from ..documents import parse_report_upload
from ..llm import LLMSettings
from ..queueing import JobQueue
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
    ReportListItem,
    ReportResponse,
)


def create_app(database_path: str | Path = DEFAULT_DATABASE_PATH) -> FastAPI:
    app = FastAPI(
        title="Golden Repo Retriever",
        version="0.1.0",
        description="Local finance-report workflow API for company metrics and summaries.",
    )
    store: AnalysisStore | None = None
    queue: JobQueue | None = None
    static_dir = Path(__file__).resolve().parents[3] / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    def get_store() -> AnalysisStore:
        nonlocal store
        if store is None:
            store = AnalysisStore(database_path)
        return store

    def get_queue() -> JobQueue:
        nonlocal queue
        if queue is None:
            queue = JobQueue(database_path)
        return queue

    def report_text_from_payload(report_id: int | None, report_text: str | None) -> tuple[str | None, str | None]:
        if report_id is None:
            return report_text, None
        report = get_store().get_report(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        return report["text"], f"report:{report_id}"

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
                "report_library": True,
                "evidence": True,
                "llm_provider": llm_settings.provider,
                "llm_enabled": bool(llm_settings.api_key),
            },
        )

    @app.post("/api/v1/analyze", response_model=AnalyzeResponse)
    def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
        report_text, report_source = report_text_from_payload(payload.report_id, payload.report_text)
        result = run_analysis(payload.query, report_text=report_text, llm_provider=payload.llm_provider)
        if report_source:
            result["report_source"] = report_source
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

    @app.post("/api/v1/reports", response_model=ReportResponse, status_code=201)
    async def create_report(file: UploadFile = File(...)) -> ReportResponse:
        try:
            report_text, source = parse_report_upload(file.filename or "report.txt", await file.read())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        report_id = get_store().save_report(
            filename=file.filename or source,
            source=source,
            text=report_text,
            content_type=file.content_type,
        )
        report = get_store().get_report(report_id)
        assert report is not None
        return ReportResponse(**report)

    @app.get("/api/v1/reports", response_model=list[ReportListItem])
    def list_reports(limit: int = 20) -> list[ReportListItem]:
        safe_limit = max(1, min(limit, 100))
        return [ReportListItem(**item) for item in get_store().list_reports(limit=safe_limit)]

    @app.get("/api/v1/reports/{report_id}", response_model=ReportResponse)
    def get_report(report_id: int) -> ReportResponse:
        report = get_store().get_report(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        return ReportResponse(**report)

    @app.post("/api/v1/jobs", response_model=JobResponse, status_code=202)
    def create_job(payload: JobRequest) -> JobResponse:
        active_store = get_store()
        job_id = get_queue().enqueue(
            query=payload.query,
            report_text=payload.report_text,
            report_id=payload.report_id,
            llm_provider=payload.llm_provider,
        )
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

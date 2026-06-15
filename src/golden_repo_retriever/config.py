from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    database_path: Path
    api_host: str
    api_port: int
    worker_poll_seconds: float
    default_llm_provider: str
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=os.getenv("APP_NAME") or "Golden Repo Retriever",
            app_version=os.getenv("APP_VERSION") or "0.1.0",
            database_path=Path(os.getenv("DATABASE_PATH") or PROJECT_ROOT / "data" / "golden_repo_retriever.db"),
            api_host=os.getenv("API_HOST") or "127.0.0.1",
            api_port=int(os.getenv("API_PORT") or "8000"),
            worker_poll_seconds=float(os.getenv("WORKER_POLL_SECONDS") or "2.0"),
            default_llm_provider=(os.getenv("LLM_PROVIDER") or "local").strip().lower(),
            log_level=(os.getenv("LOG_LEVEL") or "INFO").upper(),
        )


settings = Settings.from_env()

from __future__ import annotations

from golden_repo_retriever.config import settings
from golden_repo_retriever.logging_utils import configure_logging
from golden_repo_retriever.worker import JobWorker


def main() -> None:
    configure_logging()
    JobWorker().run_forever(poll_seconds=settings.worker_poll_seconds)


if __name__ == "__main__":
    main()

from __future__ import annotations

import uvicorn

from golden_repo_retriever.config import settings
from golden_repo_retriever.logging_utils import configure_logging


def main() -> None:
    configure_logging()
    uvicorn.run("golden_repo_retriever.api.app:app", host=settings.api_host, port=settings.api_port, reload=False)


if __name__ == "__main__":
    main()

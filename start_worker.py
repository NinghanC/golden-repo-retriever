from __future__ import annotations

from golden_repo_retriever.worker import JobWorker


def main() -> None:
    JobWorker().run_forever()


if __name__ == "__main__":
    main()

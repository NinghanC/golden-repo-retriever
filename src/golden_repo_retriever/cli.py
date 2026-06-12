from __future__ import annotations

import argparse
import json
from pathlib import Path

from .reporting import export_result
from .workflow import run_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Golden Repo Retriever workflow.")
    parser.add_argument(
        "--query",
        default="Compare Apple and Microsoft on supply chain risk and R&D investment.",
        help="Analysis query.",
    )
    parser.add_argument("--file", default=None, help="Optional UTF-8 text report to include in the analysis.")
    parser.add_argument("--output", default=None, help="Optional path to save the full analysis result as JSON.")
    parser.add_argument(
        "--llm-provider",
        choices=["local", "openai", "mistral", "custom"],
        default=None,
        help="Optional summarization provider. Defaults to LLM_PROVIDER or local.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    args = parser.parse_args()

    report_path = str(Path(args.file)) if args.file else None
    result = run_analysis(args.query, report_path=report_path, llm_provider=args.llm_provider)
    if args.output:
        export_path = export_result(result, args.output)
        result["export_path"] = export_path

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("Golden Repo Retriever")
    print(f"Companies: {', '.join(result['companies'])}")
    print(f"Summary: {result['summary']}")
    print(f"Audit events: {len(result['audit_log'])}")
    if args.output:
        print(f"Saved: {result['export_path']}")


if __name__ == "__main__":
    main()

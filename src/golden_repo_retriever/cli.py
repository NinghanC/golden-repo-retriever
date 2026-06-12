from __future__ import annotations

import argparse
import json

from .workflow import run_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Golden Repo Retriever workflow.")
    parser.add_argument(
        "--query",
        default="Compare Apple and Microsoft on supply chain risk and R&D investment.",
        help="Analysis query.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    args = parser.parse_args()

    result = run_analysis(args.query)
    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("Golden Repo Retriever")
    print(f"Companies: {', '.join(result['companies'])}")
    print(f"Summary: {result['summary']}")
    print(f"Audit events: {len(result['audit_log'])}")


if __name__ == "__main__":
    main()

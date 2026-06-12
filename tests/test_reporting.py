from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from golden_repo_retriever.reporting import export_result


class ReportingTestCase(unittest.TestCase):
    def test_export_result_writes_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "analysis.json"
            exported = export_result({"summary": "ok"}, str(output_path))

            self.assertEqual(exported, str(output_path))
            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["summary"], "ok")


if __name__ == "__main__":
    unittest.main()

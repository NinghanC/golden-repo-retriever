from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import fitz

from golden_repo_retriever.documents import parse_report_file, parse_report_upload


class DocumentsTestCase(unittest.TestCase):
    def test_parse_text_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = Path(tmp_dir) / "report.txt"
            report_path.write_text("Microsoft supply chain risk remains low.", encoding="utf-8")

            text, source = parse_report_file(str(report_path))

        self.assertIn("Microsoft", text)
        self.assertTrue(source.endswith("report.txt"))

    def test_parse_pdf_upload(self) -> None:
        pdf = fitz.open()
        page = pdf.new_page()
        page.insert_text((72, 72), "Apple R&D investment remains strong.")
        content = pdf.tobytes()
        pdf.close()

        text, source = parse_report_upload("apple_report.pdf", content)

        self.assertEqual(source, "apple_report.pdf")
        self.assertIn("Apple", text)


if __name__ == "__main__":
    unittest.main()

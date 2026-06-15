from __future__ import annotations

import unittest

from golden_repo_retriever.market_data import get_market_snapshot, get_market_snapshots


class MarketDataTestCase(unittest.TestCase):
    def test_get_market_snapshot_for_known_company(self) -> None:
        snapshot = get_market_snapshot("Apple")

        self.assertEqual(snapshot["ticker"], "AAPL")
        self.assertEqual(snapshot["currency"], "USD")
        self.assertEqual(snapshot["source"], "local")
        self.assertIn("as_of", snapshot)

    def test_get_market_snapshots_for_companies(self) -> None:
        snapshots = get_market_snapshots(["Apple", "Microsoft"])

        self.assertEqual(snapshots["Apple"]["ticker"], "AAPL")
        self.assertEqual(snapshots["Microsoft"]["ticker"], "MSFT")


if __name__ == "__main__":
    unittest.main()

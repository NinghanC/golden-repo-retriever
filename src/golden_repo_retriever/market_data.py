from __future__ import annotations

from datetime import UTC, datetime


LOCAL_MARKET_DATA = {
    "Apple": {
        "ticker": "AAPL",
        "price": 212.5,
        "market_cap": 3_250.0,
        "currency": "USD",
    },
    "Microsoft": {
        "ticker": "MSFT",
        "price": 431.2,
        "market_cap": 3_210.0,
        "currency": "USD",
    },
}


def get_market_snapshot(company: str) -> dict[str, float | str]:
    snapshot = LOCAL_MARKET_DATA.get(company)
    if snapshot is None:
        return {
            "ticker": "N/A",
            "price": 0.0,
            "market_cap": 0.0,
            "currency": "USD",
            "as_of": _timestamp(),
            "source": "local",
        }
    return {
        **snapshot,
        "as_of": _timestamp(),
        "source": "local",
    }


def get_market_snapshots(companies: list[str]) -> dict[str, dict[str, float | str]]:
    return {company: get_market_snapshot(company) for company in companies}


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()

from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app


def test_backtest_endpoint_runs_portfolio_backtest(monkeypatch) -> None:
    raw_data = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
            "Open": [100.0, 95.0, 110.0],
            "High": [100.0, 95.0, 110.0],
            "Low": [100.0, 95.0, 110.0],
            "Close": [100.0, 95.0, 110.0],
            "Adj Close": [100.0, 95.0, 110.0],
            "Volume": [1000000, 1000000, 1000000],
        }
    ).set_index("Date")

    monkeypatch.setattr("app.domain.stock.yf.download", lambda **kwargs: raw_data)

    response = TestClient(app).post(
        "/api/backtest",
        json={
            "ticker": "aapl",
            "start_date": date(2024, 1, 1).isoformat(),
            "end_date": date(2024, 1, 5).isoformat(),
            "initial_capital": 1000,
            "data_type": "daily",
            "strategies": [
                {
                    "name": "buy_one_share",
                    "condition": {
                        "type": "date_gap",
                        "gap": 10,
                    },
                    "action": "BUY",
                    "sizing": {
                        "type": "fixed_shares",
                        "unit": 1,
                    },
                }
            ],
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["summary"]["initial_capital"] == 1000
    assert body["summary"]["trade_count"] == 1
    assert body["daily_values"][-1]["total_value"] == 1010
    assert body["trades"][0]["side"] == "BUY"

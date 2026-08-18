from datetime import date

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app


def test_prices_endpoint_returns_stock_price_data(monkeypatch) -> None:
    raw_data = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-02"]),
            "Open": [100.0],
            "High": [102.0],
            "Low": [99.0],
            "Close": [101.0],
            "Adj Close": [100.5],
            "Volume": [1000000],
        }
    ).set_index("Date")

    monkeypatch.setattr("app.domain.stock.yf.download", lambda **kwargs: raw_data)

    response = TestClient(app).get(
        "/api/prices",
        params={
            "stock_name": "aapl",
            "start": date(2024, 1, 1).isoformat(),
            "end": date(2024, 1, 5).isoformat(),
            "data_type": "daily",
        },
    )

    assert response.status_code == 200
    assert response.json()["stock_name"] == "AAPL"
    assert response.json()["data_type"] == "daily"
    assert response.json()["row_count"] == 1
    assert response.json()["prices"][0]["date"] == "2024-01-02"

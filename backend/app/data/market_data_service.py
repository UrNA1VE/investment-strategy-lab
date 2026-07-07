from app.domain.asset import Asset


class MarketDataService:
    def get_price_data(self, asset: Asset, start_date: str, end_date: str) -> list[dict]:
        raise NotImplementedError("Market data ingestion will be implemented in Phase 1.")

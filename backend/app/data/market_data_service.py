from datetime import date

from app.domain.stock import Stock, StockFactory


class MarketDataService:
    def get_stock(
        self,
        stock_name: str,
        start_date: date,
        end_date: date,
        data_type: str = "daily",
    ) -> Stock:
        return StockFactory.create(
            stock_name=stock_name,
            start_date=start_date,
            end_date=end_date,
            data_type=data_type,
        )

    def get_price_records(
        self,
        stock_name: str,
        start_date: date,
        end_date: date,
        data_type: str = "daily",
    ) -> list[dict]:
        stock = self.get_stock(
            stock_name=stock_name,
            start_date=start_date,
            end_date=end_date,
            data_type=data_type,
        )
        return stock.to_records()

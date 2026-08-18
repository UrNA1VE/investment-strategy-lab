from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from app.data.market_data_service import MarketDataService
from app.domain.stock import StockDataError
from app.models.responses import PriceDataResponse

router = APIRouter(prefix="/api", tags=["prices"])


def get_market_data_service() -> MarketDataService:
    return MarketDataService()


@router.get("/prices", response_model=PriceDataResponse)
def get_prices(
    stock_name: str = Query(min_length=1, examples=["AAPL"]),
    start: date = Query(examples=["2024-01-01"]),
    end: date = Query(examples=["2024-01-31"]),
    data_type: str = Query(default="daily", examples=["daily"]),
    market_data_service: MarketDataService = Depends(get_market_data_service),
) -> PriceDataResponse:
    try:
        stock = market_data_service.get_stock(
            stock_name=stock_name,
            start_date=start,
            end_date=end,
            data_type=data_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return PriceDataResponse(
        stock_name=stock.stock_name,
        start_date=stock.start_date,
        end_date=stock.end_date,
        data_type=stock.data_type,
        row_count=len(stock.data),
        prices=stock.to_records(),
    )

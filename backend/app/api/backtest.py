from fastapi import APIRouter, HTTPException

from app.domain.portfolio import Portfolio
from app.domain.stock import StockDataError, StockFactory
from app.models.requests import BacktestRequest
from app.models.responses import BacktestResponse, DailyValueResponse, TradeResponse
from app.strategies.strategy import StrategyFactory

router = APIRouter(prefix="/api", tags=["backtest"])


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest) -> BacktestResponse:
    # Load market data for the requested ticker and date range.
    try:
        stock = StockFactory.create(
            stock_name=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            data_type=request.data_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Create a portfolio that owns cash, positions, trades, and daily values.
    portfolio = Portfolio(cash=request.initial_capital)

    # Convert user strategy configs into RuleStrategy objects.
    try:
        for strategy_config in request.strategies:
            portfolio.add_strategy(
                strategy_config.name,
                StrategyFactory.create(
                    stock=stock,
                    portfolio=portfolio,
                    config=strategy_config.model_dump(),
                ),
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Run the daily backtest loop and collect portfolio values.
    daily_values = portfolio.run()
    if isinstance(daily_values, str):
        raise HTTPException(status_code=400, detail=daily_values)

    # Convert pandas rows and domain objects into JSON-friendly response models.
    return BacktestResponse(
        summary=portfolio.summary(),
        daily_values=[
            DailyValueResponse(
                date=row.date,
                cash=float(row.cash),
                positions_value=float(row.positions_value),
                total_value=float(row.total_value),
            )
            for row in daily_values.itertuples(index=False)
        ],
        trades=[
            TradeResponse(
                stock_name=trade.stock_name,
                trade_date=trade.trade_date,
                side=trade.side.value,
                quantity=int(trade.quantity),
                price=float(trade.price),
                trade_detail=trade.trade_detail,
            )
            for trade in portfolio.trades
        ],
    )

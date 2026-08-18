# Architecture

This project is structured as a backend-first cloud data analytics application.

## Layers

- API layer: FastAPI routes and request validation
- Service layer: workflow orchestration
- Domain layer: class-based business objects
- Data layer: market data ingestion, ETL, and caching
- Deployment layer: Docker, Azure, and CI/CD documentation

## Domain Objects

- Account
- Stock
- Portfolio
- Trade
- BacktestRun
- BaseStrategy
- BacktestEngine
- MetricsCalculator

## Stock Data Model

The market data layer is centered on a `Stock` abstract base class. A stock instance receives:

- stock name
- start date
- end date
- data type, such as `daily` or `hourly`

When a concrete stock class is initialized, it loads data from yfinance and standardizes the result into OHLCV records.

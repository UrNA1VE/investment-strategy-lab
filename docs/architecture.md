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
- Asset
- Portfolio
- Trade
- BacktestRun
- BaseStrategy
- BacktestEngine
- MetricsCalculator

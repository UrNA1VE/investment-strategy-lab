# Cloud Investment Strategy Lab

Cloud Investment Strategy Lab is a cloud-ready data analytics project for running simple rule-based investment backtests with public market data. The project uses stock data as an accessible dataset, while the main focus is backend architecture, data ingestion, ETL, caching, containerization, and cloud deployment.

## MVP Goal

The first version will allow a user to:

1. Select a stock ticker.
2. Select a date range.
3. Select a simple trading strategy.
4. Run a backtest.
5. View portfolio metrics, equity curve data, and trade records.

## Architecture Direction

```text
Frontend
Simple form and results dashboard
        |
        v
FastAPI Backend
API routes and request validation
        |
        v
Service Layer
Backtest orchestration
        |
        v
Domain Layer
Account, Asset, Portfolio, Trade, Strategy, BacktestRun
        |
        v
Data Layer
Market data source, ETL, cache
        |
        v
Cloud
Docker, Azure Container Apps, Azure Static Web Apps, GitHub Actions
```

## Why Class-Based Design

The backend starts with class-based domain objects so the system can later support multiple accounts, multiple stocks, multiple strategies, saved backtest runs, and additional metrics without rewriting the core engine.

## Current Phase

Phase 0 creates the project foundation:

- Monorepo folder structure
- FastAPI backend skeleton
- Health check endpoint
- Class-based domain object placeholders
- Initial documentation

## Local Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "cloud-investment-strategy-lab"
}
```

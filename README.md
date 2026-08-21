# Cloud Investment Strategy Lab

Cloud Investment Strategy Lab is a containerized data analytics project for running simple rule-based investment backtests with public market data. It uses a FastAPI backend, a Streamlit frontend, Docker, GitHub Actions, Azure Container Registry, and Azure Container Apps.

## Completed Features

- Fetch daily or hourly stock price data from yfinance.
- Run a rule-based backtest through a FastAPI endpoint.
- Configure buy and sell trading rules from a Streamlit page.
- View two result charts: stock price and portfolio value.
- Run the backend and frontend locally as separate services.
- Run the backend and frontend locally with Docker Compose.
- Deploy backend and frontend containers to Azure Container Apps.
- Build and push Docker images through a manual GitHub Actions workflow.

## Architecture

```text
Streamlit Frontend
One-page input form and result charts
        |
        v
FastAPI Backend
API routes and request validation
        |
        v
Domain Layer
Stock, Account, Portfolio, Trade, RuleStrategy
        |
        v
Market Data
yfinance stock price data
        |
        v
Cloud
Docker, Azure Container Registry, Azure Container Apps, GitHub Actions
```

## Why Class-Based Design

The backend uses class-based domain objects for accounts, stocks, portfolios, trades, conditions, sizing, and rule strategies. This keeps the current version small while making the core backtesting logic easier to extend.

## Backend

The FastAPI backend includes:

- Health check endpoint
- Price data endpoint
- Backtest endpoint
- `Stock` base class
- `DailyStock` and `HourlyStock`
- `Portfolio` daily backtest loop
- `RuleStrategy` with condition, action, and sizing
- Portfolio and account summary methods

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

## Price Data Endpoint

```text
GET /api/prices?stock_name=AAPL&start=2024-01-01&end=2024-01-31&data_type=daily
```

Supported `data_type` values:

- `daily`
- `hourly`

## Local Frontend Setup

Start the backend first, then run Streamlit from the project root:

```bash
source backend/.venv/bin/activate
pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py
```

Then open:

```text
http://127.0.0.1:8501
```

## Docker Compose

Run both services locally:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

## Azure Deployment

The project has been deployed with:

- Azure Container Registry: `qkwinvestmentlabacr`
- Backend Azure Container App: `investment-strategy-backend`
- Frontend Azure Container App: `investment-strategy-frontend`
- Resource group: `portfolio-rg`

The repository includes a manual GitHub Actions workflow for building and
deploying the backend and frontend Docker images:

```text
.github/workflows/deploy-azure-container-apps.yml
```

Setup notes live in:

```text
deployment/github-actions-azure.md
```

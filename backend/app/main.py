from fastapi import FastAPI

from app.api.backtest import router as backtest_router
from app.api.health import router as health_router
from app.api.prices import router as prices_router


# FastAPI is the HTTP entry point for the backend service.
app = FastAPI(
    title="Cloud Investment Strategy Lab API",
    description="Backend API for a cloud-ready investment strategy backtesting platform.",
    version="0.1.0",
)

# Routers group related endpoints into small files.
app.include_router(health_router)
app.include_router(prices_router)
app.include_router(backtest_router)

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.prices import router as prices_router


app = FastAPI(
    title="Cloud Investment Strategy Lab API",
    description="Backend API for a cloud-ready investment strategy backtesting platform.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(prices_router)

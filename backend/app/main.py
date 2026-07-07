from fastapi import FastAPI

from app.api.health import router as health_router


app = FastAPI(
    title="Cloud Investment Strategy Lab API",
    description="Backend API for a cloud-ready investment strategy backtesting platform.",
    version="0.1.0",
)

app.include_router(health_router)

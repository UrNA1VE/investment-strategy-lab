from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    # Simple endpoint used to confirm that the API server is running.
    return {
        "status": "ok",
        "service": "cloud-investment-strategy-lab",
    }

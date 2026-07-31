from fastapi import APIRouter, status

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    return {"status": "ok", "service": "ingestion-api"}

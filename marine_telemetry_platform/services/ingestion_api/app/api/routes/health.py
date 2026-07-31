from fastapi import APIRouter, status


router = APIRouter(
    prefix = "/health",
    tags = ["health"],
)

@router.get("/live", status_code=HTTP_200_OK)
async def liveness() -> dict[str,str]:
    return {"status":"OK","service":"ingestion-api"}

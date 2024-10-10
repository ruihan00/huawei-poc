from fastapi import APIRouter

router = APIRouter(prefix="/server")

@router.get("/healthcheck")
async def healthcheck():
    return {"message": "CCTV System Server is Running"}

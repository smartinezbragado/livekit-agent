from fastapi.routing import APIRouter
from fastapi import HTTPException
from starlette.responses import JSONResponse
from livekit.api import AccessToken, VideoGrants
import os


router = APIRouter(prefix="/token", tags=["token"])

@router.post("", include_in_schema=False)
@router.post("/")
async def get_token(identity: str):
    if not identity:
        raise HTTPException(status_code=400, detail="Identity is required")

    grant = VideoGrants(room_join=True, room="recruit")
    access_token = AccessToken(
        os.environ["LIVEKIT_API_KEY"],
        os.environ["LIVEKIT_API_SECRET"],
    ).with_identity("identity") \
    .with_name("name") \
    .with_grants(grant)
    token = access_token.to_jwt()
    return JSONResponse({"token": token})
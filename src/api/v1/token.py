import os
import random
from fastapi.routing import APIRouter
from fastapi import HTTPException
from starlette.responses import JSONResponse
from livekit.api import AccessToken, VideoGrants

router = APIRouter(prefix="/token", tags=["token"])


@router.get("/")
async def get_token():

    if not os.environ.get("LIVEKIT_API_KEY") or not os.environ.get("LIVEKIT_API_SECRET") or not os.environ.get("LIVEKIT_URL"):
        raise HTTPException(
            status_code=500, detail="LiveKit environment variables are not set"
        )
    
    participant_identity = f"voice_assistant_user_{random.randint(0, 10000)}"
    
    grant = VideoGrants(
        room_join=True, 
        room="voice_assistant_room",
        can_publish=True,
        can_publish_data=True,
        can_subscribe=True
    )
    token = AccessToken(
        os.environ["LIVEKIT_API_KEY"],
        os.environ["LIVEKIT_API_SECRET"],
    ).with_identity(participant_identity) \
    .with_grants(grant) \
    .to_jwt()

    return JSONResponse({
        "serverUrl": os.environ.get("LIVEKIT_URL"),
        "roomName": "voice_assistant_room",
        "participantToken": token,
        "participantName": participant_identity,
    })
from fastapi import APIRouter, HTTPException
from src.api.v1.schemas import EmailRequest
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from loguru import logger

router = APIRouter(prefix="/api/v1/notifications")


@router.post("/send-email")
async def send_email(request: EmailRequest):
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")

    if not SENDGRID_API_KEY or not FROM_EMAIL:
        raise HTTPException(status_code=500, detail="SendGrid not configured")

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=request.email,
        subject=request.subject,
        plain_text_content=request.content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.warning(response.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Email sent to {request.email}"}
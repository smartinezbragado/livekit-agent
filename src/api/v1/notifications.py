from fastapi import APIRouter, HTTPException
from src.api.v1.schemas import EmailRequest
import boto3
import os
from loguru import logger

router = APIRouter(prefix="/api/v1/notifications")


@router.post("/send-email")
async def send_email(request: EmailRequest):

    # Create an SES client
    ses_client = boto3.client('ses', region_name='eu-north-1')
    try:
        response = ses_client.send_email(
            Source=os.environ["SENDER_EMAIL"],
            Destination={
                'ToAddresses': [request.email],
            },
            Message={
                'Subject': {
                    'Data': request.subject,
                },
                'Body': {
                    'Text': {
                        'Data': request.content,
                    },
                },
            }
        )
        logger.warning(response)
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"Email sent to {request.email}"}
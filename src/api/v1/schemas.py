from pydantic import BaseModel, EmailStr
from fastapi import UploadFile

class EmailRequest(BaseModel):
    email: EmailStr
    subject: str
    content: str
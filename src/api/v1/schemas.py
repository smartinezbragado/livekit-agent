from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    email: EmailStr
    subject: str
    content: str

class JobDescriptionRequest(BaseModel):
    job_description: str
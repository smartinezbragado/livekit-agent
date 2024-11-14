from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from pydantic import EmailStr
import os
import shutil
from openai import OpenAI
from loguru import logger

openai_client = OpenAI()

router = APIRouter(prefix="/api/v1/talent")

@router.post("/generate-prompt")
async def generate_prompt(
    email: EmailStr = Form(...),
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENAI_BASE_URL or not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Openai not configured")

    system_prompt = """
    ### Your Role

    You are a proffessional AI Prompt Generator.

    ### Your mision

    Generate prompts for Talent Acquisition Managers that need to make an interview to candidates based on a given job description.
    The prompts must contain the role of the AI, the Mision and the expected behaviour

    ### Interview Procedure

    1. Welcome and explain the company and its culture to the interviewee.
    2. Ask detailed questions to determine if the candidate has a cultural and technical fit.
    3. Ask follow-up questions to really understand the level of seniority of the interviewee in the skills required in the job description.
    4. If the candidate behaves badly or does not answer well, politely conclude the conversation with a positive message.

    ### Rules

    1. Create the system prompt in markdown
    2. Generate directly the prompt, do not add additional commments
    """
    user_prompt = f"Job Description: {job_description}"

    with open(resume.filename, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        logger.info(response)
        generated_prompt = response.choices[0].message.content
        return {"system_prompt": generated_prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

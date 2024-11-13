from fastapi import APIRouter, HTTPException
import requests
import os
from src.api.v1.schemas import JobDescriptionRequest
from openai import OpenAI
from loguru import logger

openai_client = OpenAI()

router = APIRouter(prefix="/talent")

@router.post("/generate-prompt")
async def generate_prompt(request: JobDescriptionRequest):
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
    user_prompt = f"Job Description: {request.job_description}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

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

# chat_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat_ai(request: ChatRequest):
    """
    Connects to Perplexity AI to generate a relevant and contextual response.
    """
    if not PERPLEXITY_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured.")

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are an intelligent AI assistant integrated into a social media platform."},
            {"role": "user", "content": request.message},
        ],
        "max_tokens": 400,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return {"reply": data["choices"][0]["message"]["content"]}
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

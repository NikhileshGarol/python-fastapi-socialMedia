from fastapi import APIRouter, HTTPException
from mcp_server.tools.summarize_tool import summarize_text
from mcp_server.tools.sentiment_tool import analyze_sentiment

router = APIRouter()

@router.post("/summarize/invoke")
def invoke_summarize(payload: dict):
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    # you can use context as well
    summary = summarize_text(text)
    return {"summary": summary}

@router.post("/sentiment/invoke")
def invoke_sentiment(payload: dict):
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    result = analyze_sentiment(text)
    return result
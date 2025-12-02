import json
from typing import Any, Dict

from fastapi import HTTPException

from mcp_server.services.llm_service import get_client


def _parse_sentiment_payload(raw: str) -> Dict[str, Any]:
    """
    Attempt to parse the model response into a structured payload.
    Falls back to treating the raw string as the sentiment label.
    """
    raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"sentiment": raw}

    sentiment = (
        data.get("sentiment")
        or data.get("label")
        or data.get("value")
        or raw
    )

    payload: Dict[str, Any] = {"sentiment": str(sentiment).strip()}

    if "reason" in data:
        payload["reason"] = str(data["reason"]).strip()
    if "confidence" in data:
        try:
            payload["confidence"] = float(data["confidence"])
        except (TypeError, ValueError):
            pass

    return payload


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Uses Perplexity Sonar to classify sentiment and return a structured payload.
    """
    if not text:
        raise HTTPException(status_code=400, detail="No content provided for sentiment analysis.")

    prompt = (
        "Analyze the sentiment of the text below. "
        "Respond strictly in JSON with the shape:\n"
        '{"sentiment": "Positive|Neutral|Negative", "reason": "short justification", "confidence": 0-1}\n\n'
        f"Text:\n{text}"
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.0,
        )
        content = response.choices[0].message.content or ""
        parsed = _parse_sentiment_payload(content)

        # ALWAYS return JSON string
        return json.dumps(parsed, indent=2)
    
    except HTTPException:
        raise
    except Exception as exc:
        print("Sentiment API Error:", exc)
        raise HTTPException(status_code=500, detail="Sentiment analysis failed.")

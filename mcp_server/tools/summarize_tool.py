import os
from openai import OpenAI
from fastapi import HTTPException

# Ensure .env was loaded before this import in main.py
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


def get_client():
    """
    Returns a Perplexity OpenAI-compatible client.
    Raises an error if API key is missing.
    """
    if not PERPLEXITY_API_KEY:
        raise RuntimeError("PERPLEXITY_API_KEY missing. Set it in the .env file.")

    return OpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai"
    )


def summarize_text(text: str) -> str:
    """
    Uses Perplexity Sonar to summarize text.
    """
    if not text:
        raise HTTPException(status_code=400, detail="No text to summarize.")

    prompt = f"Summarize the following text in 3–5 sentences:\n\n{text}"

    try:
        client = get_client()

        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Perplexity API error:", e)
        raise HTTPException(status_code=500, detail="Summarization failed.")

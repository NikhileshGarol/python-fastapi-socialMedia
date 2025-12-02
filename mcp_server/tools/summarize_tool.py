from fastapi import HTTPException

from mcp_server.services.llm_service import get_client


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

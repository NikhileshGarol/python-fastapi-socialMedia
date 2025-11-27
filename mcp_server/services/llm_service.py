import os
from openai import OpenAI
from fastapi import HTTPException

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


def get_client():
    if not PERPLEXITY_API_KEY:
        raise RuntimeError("PERPLEXITY_API_KEY missing. Configure it properly.")

    return OpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai"
    )


class LLMService:

    @staticmethod
    async def summarize_text(text: str):
        client = get_client()

        prompt = f"Summarize the following content:\n\n{text}"

        try:
            response = client.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.2,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(500, f"Summarization failed: {e}")


    @staticmethod
    async def analyze_sentiment(text: str):
        client = get_client()

        prompt = f"""
        Analyze the sentiment of this text and classify as:
        Positive, Neutral, or Negative.
        
        Text: {text}
        """

        try:
            response = client.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(500, f"Sentiment analysis failed: {e}")

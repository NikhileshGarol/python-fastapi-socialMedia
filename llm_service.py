# app/services/llm_service.py

import os
from openai import OpenAI
from fastapi import HTTPException

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

client = OpenAI(
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai"  # CORRECT
)

class LLMService:

    @staticmethod
    def summarize_text(text: str) -> str:
        """Synchronous summarizer – compatible with FastAPI threadpool."""
        if not text:
            raise HTTPException(400, "No content provided for summarization.")

        prompt = (
            "Summarize the following text in a concise and clear manner:\n\n"
            f"{text}"
        )

        try:
            response = client.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.2,
            )

            return response.choices[0].message.content

        except Exception as e:
            print("Perplexity API error:", e)
            raise HTTPException(500, "AI summarization failed.")

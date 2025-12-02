from fastapi import HTTPException
from mcp_server.services.llm_service import get_client
import re


def is_context_meaningful(text: str) -> bool:
    text = text.strip()

    if len(text) < 15:
        return False

    generic_inputs = ["some context", "context", "test", "hello", "hi", "ok", "nothing"]
    if text.lower() in generic_inputs:
        return False

    gibberish_pattern = r"^(.)\1{5,}$"
    if re.match(gibberish_pattern, text):
        return False

    return True


def generate_content(context: str) -> str:
    if not context:
        raise HTTPException(
            status_code=400,
            detail="No context provided. Please provide more details."
        )

    if not is_context_meaningful(context):
        raise HTTPException(
            status_code=422,
            detail="The provided context is too vague or unclear to generate useful content. Please provide a more detailed context."
        )

    prompt = f"""
    You are a content generator.
    If the context is vague, DO NOT ask questions or request more details.
    Always generate a structured short blog post based on the context below.

    Context: {context}

    Return only the content. No disclaimers. No suggestions. 
    """

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )

        ai_output = response.choices[0].message.content.strip()

        if not ai_output or len(ai_output) < 30:
            raise HTTPException(
                status_code=422,
                detail="Unable to generate meaningful content from the given context. Please refine your input."
            )

        return ai_output

    except Exception as e:
        print("Perplexity API error:", e)
        raise HTTPException(
            status_code=500,
            detail="Content generation failed due to an internal error."
        )

from fastapi import HTTPException

from mcp_server.services.llm_service import get_client


def chat_reply(message: str) -> dict:
    """
    Simple chat tool that mirrors the old /chat endpoint, exposed via MCP.

    Args:
        message: User's message text.

    Returns:
        {"reply": <assistant_reply>}
    """
    if not message:
        raise HTTPException(status_code=400, detail="Message is required.")

    prompt = (
        "You are an intelligent AI assistant integrated into a social media platform.\n"
        "Respond helpfully and concisely to the following message:\n\n"
        f"{message}"
    )

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        reply = response.choices[0].message.content
        return {"reply": reply}
    except Exception as exc:
        print("Chat MCP tool error:", exc)
        raise HTTPException(status_code=500, detail="Chat AI failed.")

{
  "cells": [],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}
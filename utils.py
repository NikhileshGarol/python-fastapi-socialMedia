from passlib.context import CryptContext
from fastapi import HTTPException
import json
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password


def hash_password(password: str):
    return pwd_context.hash(password)

# Verify the password


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def standard_error_format(status: int, message: str):
    return HTTPException(
        status_code=status,
        detail={
            "error": True,
            "statusCode": status,
            "message": message
        }
    )


def extract_mcp_error_message(raw: str) -> str:
    """
    Extracts clean message from MCP tool error string.
    Expected pattern:
      "MCP tool 'x' failed with 422: {\"detail\": \"msg\"}"
    """
    try:
        # Extract JSON substring using regex
        json_match = re.search(r"\{.*\}", raw)
        if json_match:
            error_json = json.loads(json_match.group(0))
            return error_json.get("detail", raw)
    except:
        pass

    # Fallback to raw trimmed string
    return raw

# utils_openai.py
import os
import asyncio
from openai import OpenAI


MODEL_FOR_STREAM = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
PERSONALITY_PROMPT = (
    "You are Aira, the user's caring best friend. Warm, empathetic, funny in a light way. "
    "Always validate emotions, avoid judgement, avoid long explanations, and use short comforting examples and gentle guidance. "
    "You may use 1-2 light emojis to convey tone."
)

def get_openai_client():
    
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_response(resp):
    """
    Safely extract assistant text from a Responses API response.

    Looks for the first output item of type 'message', then returns
    its first content.text. Falls back to string(resp) if needed.
    """
    try:
        # New Responses API: resp.output is a list of items
        # We want the one with type == "message"
        for item in getattr(resp, "output", []) or []:
            if getattr(item, "type", None) == "message":
                content_list = getattr(item, "content", []) or []
                if content_list and hasattr(content_list[0], "text"):
                    return content_list[0].text

        # Fallback: try the last output item
        if getattr(resp, "output", None):
            last = resp.output[-1]
            content_list = getattr(last, "content", []) or []
            if content_list and hasattr(content_list[0], "text"):
                return content_list[0].text
    except Exception:
        pass

    # Last resort: stringified response
    return str(resp)

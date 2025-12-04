# # utils_openai.py

# from openai import OpenAI
# import os

# def get_openai_client():
#     return OpenAI(api_key=os.getenv("OPENAI_API_KEY", ))

import os
import json
import asyncio
from openai import OpenAI
from memory.services import get_recent_messages_as_list, get_or_create_user_memory

MODEL_FOR_STREAM = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
PERSONALITY_PROMPT = (
    "You are Aira, the user's caring best friend. Warm, empathetic, funny in a light way. "
    "Always validate emotions, avoid judgement, and use short comforting examples and gentle guidance. "
    "You may use 1-2 light emojis to convey tone."
)

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def stream_openai_response(external_id, user_msg, send_chunk_callback):
    """
    external_id: user identifier (string)
    user_msg: the latest user message (string)
    send_chunk_callback: async function that accepts a dict to send to frontend
    """

    # Build messages (system + memory + recent messages + new user input)
    system = {"role": "system", "content": PERSONALITY_PROMPT}

    recent_msgs = get_recent_messages_as_list(external_id, limit=30)  # list of dicts {role, content}

    # append a small summarized memory snippet if exists
    um = get_or_create_user_memory(external_id)
    mem_snippet = ""
    try:
        if um.facts.get("summary"):
            mem_snippet = f"User memory summary: {um.facts.get('summary')}\n"
    except Exception:
        mem_snippet = ""

    # Build the 'messages' for the Responses API
    assembled_prompt = system["content"] + "\n\n" + mem_snippet + "\n\n"
    # include a few recent messages for short-term context
    for m in recent_msgs[-10:]:
        assembled_prompt += f"{m['role']}: {m['content']}\n"
    assembled_prompt += f"user: {user_msg}\n"

    client = get_openai_client()

    # The OpenAI Python SDK might be sync. We'll call it in a thread and iterate the streaming generator.
    def blocking_stream():
        # Responses API - stream responses by passing stream=True; the SDK returns an iterator-like object
        return client.responses.stream(
            model=MODEL_FOR_STREAM,
            input=assembled_prompt,
        )

    loop = asyncio.get_event_loop()
    stream_iter = await loop.run_in_executor(None, blocking_stream)

    # stream_iter is an iterator yielding events; iterate using a thread-friendly approach
    try:
        for event in stream_iter:
            # event is typically an object with delta or output_text fragments
            # Try to extract token delta
            try:
                # Some SDKs put data under event.delta or event.output_text
                if hasattr(event, "delta") and event.delta:
                    # event.delta might be a sequence
                    text_delta = ""
                    for d in event.delta:
                        if isinstance(d, dict) and "content" in d:
                            text_delta += d["content"]
                    if text_delta:
                        # send streaming chunk
                        asyncio.create_task(send_chunk_callback({"type": "stream", "delta": text_delta}))
                elif hasattr(event, "output_text") and event.output_text:
                    # final chunk or cumulative text
                    asyncio.create_task(send_chunk_callback({"type": "final", "text": event.output_text}))
                else:
                    # sometimes event is a dict-like
                    ev = event
                    # fallback extraction:
                    txt = ""
                    if isinstance(ev, dict):
                        txt = ev.get("text") or ev.get("output_text") or ""
                        if txt:
                            asyncio.create_task(send_chunk_callback({"type": "stream", "delta": txt}))
            except Exception:
                # best-effort: send nothing on parse problems
                pass
    finally:
        # close generator if needed
        try:
            stream_iter.close()
        except Exception:
            pass


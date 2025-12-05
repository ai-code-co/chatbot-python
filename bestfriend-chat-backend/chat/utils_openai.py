# utils_openai.py
import os
import asyncio
from openai import OpenAI
from memory.services import get_recent_messages_as_list, get_or_create_user_memory

MODEL_FOR_STREAM = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
PERSONALITY_PROMPT = (
    "You are Aira, the user's caring best friend. Warm, empathetic, funny in a light way. "
    "Always validate emotions, avoid judgement, avoid long explanations, and use short comforting examples and gentle guidance. "
    "You may use 1-2 light emojis to convey tone."
)

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def stream_openai_response(external_id, user_msg, send_chunk_callback):
    """
    external_id: user identifier (string)
    user_msg: latest user message (string)
    send_chunk_callback: async function that accepts dicts to send to frontend
    """

    # Build short-term context messages
    system = {"role": "system", "content": PERSONALITY_PROMPT}
    recent_msgs = get_recent_messages_as_list(external_id, limit=30)
    um = get_or_create_user_memory(external_id)
    mem_snippet = ""
    if um.facts.get("summary"):
        mem_snippet = f"User memory summary: {um.facts.get('summary')}\n"

    assembled_prompt = system["content"] + "\n\n" + mem_snippet + "\n\n"
    for m in recent_msgs[-10:]:
        assembled_prompt += f"{m['role']}: {m['content']}\n"
    assembled_prompt += f"user: {user_msg}\n"

    def blocking_stream():
        """
        Run generator and iterate entirely in this thread.
        Use asyncio.run to call async send_chunk_callback safely.
        """
        client = get_openai_client()
        for event in client.responses.stream(model=MODEL_FOR_STREAM, input=assembled_prompt):
            try:
                out = {}
                if hasattr(event, "delta") and event.delta:
                    text = ""
                    for d in event.delta:
                        if isinstance(d, dict) and "content" in d:
                            text += d["content"]
                    if text:
                        out = {"type": "stream", "delta": text}
                elif hasattr(event, "output_text") and event.output_text:
                    out = {"type": "final", "text": event.output_text}
                else:
                    ev = event
                    if isinstance(ev, dict):
                        txt = ev.get("text") or ev.get("output_text") or ""
                        if txt:
                            out = {"type": "stream", "delta": txt}

                if out:
                    # Call async callback from sync thread
                    asyncio.run(send_chunk_callback(out))
            except Exception:
                # ignore parsing errors
                pass

    loop = asyncio.get_event_loop()
    # run the whole streaming loop in a separate thread
    await loop.run_in_executor(None, blocking_stream)


# 
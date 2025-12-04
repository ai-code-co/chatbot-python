import os
import asyncio
from django.conf import settings
from .models import UserMemory, ConversationMessage, ConversationSummary
from django.utils import timezone
from openai import OpenAI

# Config
SUMMARIZE_AFTER_MESSAGES = 25     # run a summary job after these many new messages
MAX_RAW_MESSAGES_KEEP = 200       # keep this many raw messages per user (prune older)

def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_or_create_user_memory(external_id):
    """
    external_id: a string identifier for the user (e.g. websocket client id or user.id)
    """
    um, _ = UserMemory.objects.get_or_create(external_id=external_id)
    return um

def append_message_to_memory(external_id, role, content, metadata=None):
    um = get_or_create_user_memory(external_id)
    msg = ConversationMessage.objects.create(
        user_memory=um,
        role=role,
        content=content,
        metadata=metadata or {}
    )
    # prune old messages if exceeding MAX_RAW_MESSAGES_KEEP
    msgs = ConversationMessage.objects.filter(user_memory=um).order_by('-created_at')
    if msgs.count() > MAX_RAW_MESSAGES_KEEP:
        to_delete = msgs[S_MAX_RAW_MESSAGES_KEEP:]
        ConversationMessage.objects.filter(id__in=[m.id for m in to_delete]).delete()
    return msg

def get_recent_messages_as_list(external_id, limit=50):
    um = get_or_create_user_memory(external_id)
    qs = ConversationMessage.objects.filter(user_memory=um).order_by('created_at')  # chronological
    qs = qs[(0 if qs.count() < limit else qs.count()-limit):]
    return [{"role": m.role, "content": m.content} for m in qs]

async def summarize_memory_async(external_id):
    """
    Ask the model to summarize the user's recent conversation history into a short profile.
    Runs asynchronously (so call via asyncio.to_thread).
    """
    # run synchronous DB + OpenAI calls in thread
    return await asyncio.to_thread(_summarize_memory_sync, external_id)

def _summarize_memory_sync(external_id):
    um = get_or_create_user_memory(external_id)
    messages = ConversationMessage.objects.filter(user_memory=um).order_by('-created_at')[:SUMMARIZE_AFTER_MESSAGES]
    messages = list(reversed(messages))
    raw_text = "\n".join([f"{m.role}: {m.content}" for m in messages])
    prompt = (
        "Summarize the user's recent conversation into a few short bullet points suitable for long-term memory.\n\n"
        "Conversation:\n"
        f"{raw_text}\n\n"
        "Return a short JSON object with keys: 'profile_summary', 'important_facts', 'current_concerns'. "
        "Keep each field short."
    )
    client = get_client()
    resp = client.responses.create(
        model=os.getenv("MEMORY_MODEL", "gpt-4.1-mini"),
        input=prompt,
    )
    # Responses API returns a structure — extract text
    summary_text = getattr(resp, "output_text", None) or str(resp)
    # Save into ConversationSummary and into UserMemory.facts (basic)
    cs, _ = ConversationSummary.objects.get_or_create(user_memory=um)
    cs.summary_text = summary_text
    cs.last_updated = timezone.now()
    cs.save()

    # naive parse: store raw summary under facts.summary; you can parse JSON if model returns JSON
    try:
        import json
        parsed = json.loads(summary_text)
        # store under facts
        um.facts.update(parsed if isinstance(parsed, dict) else {"summary": summary_text})
    except Exception:
        um.facts.update({"summary": summary_text})
    um.save()
    return cs

async def analyze_message_async(external_id, text):
    """Return sentiment and topics as a dict using OpenAI.
       Runs in thread."""
    return await asyncio.to_thread(_analyze_message_sync, external_id, text)

def _analyze_message_sync(external_id, text):
    client = get_client()
    prompt = (
        "Perform a short analysis of the following user message. Return a JSON object with fields:\n"
        "  - sentiment: one of {positive, neutral, negative}\n"
        "  - sentiment_score: a number between -1 and 1\n"
        "  - topics: array of short topic labels\n\n"
        f"Message: '''{text}'''"
    )
    resp = client.responses.create(
        model=os.getenv("ANALYSIS_MODEL", "gpt-4.1-mini"),
        input=prompt
    )
    out = getattr(resp, "output_text", None) or str(resp)
    try:
        import json
        parsed = json.loads(out)
        return parsed
    except Exception:
        # best-effort heuristic fallback
        return {"sentiment": "neutral", "sentiment_score": 0.0, "topics": []}

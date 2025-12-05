# memory/services.py
import os
import asyncio
from django.utils import timezone
from openai import OpenAI

# Configuration
SUMMARIZE_AFTER_MESSAGES = 25     # summarize after this many messages
MAX_RAW_MESSAGES_KEEP = 200       # prune older messages

def get_client():
    """Create OpenAI client."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_or_create_user_memory(external_id):
    """Get or create UserMemory by external_id."""
    # import models inside function to avoid AppRegistryNotReady at startup
    from .models import UserMemory
    um, _ = UserMemory.objects.get_or_create(external_id=external_id)
    return um

def append_message_to_memory(external_id, role, content, metadata=None):
    """Append a chat message to user's memory."""
    from .models import ConversationMessage
    um = get_or_create_user_memory(external_id)
    msg = ConversationMessage.objects.create(
        user_memory=um,
        role=role,
        content=content,
        metadata=metadata or {}
    )

    # prune old messages
    msgs = ConversationMessage.objects.filter(user_memory=um).order_by('-created_at')
    if msgs.count() > MAX_RAW_MESSAGES_KEEP:
        to_delete = msgs[MAX_RAW_MESSAGES_KEEP:]
        ConversationMessage.objects.filter(id__in=[m.id for m in to_delete]).delete()
    return msg

def get_recent_messages_as_list(external_id, limit=50):
    """Return recent messages as list of dicts."""
    from .models import ConversationMessage
    um = get_or_create_user_memory(external_id)
    qs = ConversationMessage.objects.filter(user_memory=um).order_by('created_at')
    qs = qs[(0 if qs.count() < limit else qs.count() - limit):]
    return [{"role": m.role, "content": m.content} for m in qs]

async def summarize_memory_async(external_id):
    """Asynchronously summarize user's recent conversation."""
    return await asyncio.to_thread(_summarize_memory_sync, external_id)

def _summarize_memory_sync(external_id):
    from .models import UserMemory, ConversationMessage, ConversationSummary

    um = get_or_create_user_memory(external_id)
    messages = ConversationMessage.objects.filter(user_memory=um).order_by('-created_at')[:SUMMARIZE_AFTER_MESSAGES]
    messages = list(reversed(messages))
    raw_text = "\n".join([f"{m.role}: {m.content}" for m in messages])

    prompt = (
        "Summarize the user's recent conversation into short bullet points suitable for long-term memory.\n\n"
        f"Conversation:\n{raw_text}\n\n"
        "Return a short JSON object with keys: 'profile_summary', 'important_facts', 'current_concerns'. "
        "Keep each field short."
    )

    client = get_client()
    resp = client.responses.create(
        model=os.getenv("MEMORY_MODEL", "gpt-5-nano"),
        input=prompt,
    )
    summary_text = getattr(resp, "output_text", None) or str(resp)

    # Save into ConversationSummary
    cs, _ = ConversationSummary.objects.get_or_create(user_memory=um)
    cs.summary_text = summary_text
    cs.last_updated = timezone.now()
    cs.save()

    # Parse JSON safely and update UserMemory.facts
    try:
        import json
        parsed = json.loads(summary_text)
        um.facts.update(parsed if isinstance(parsed, dict) else {"summary": summary_text})
    except Exception:
        um.facts.update({"summary": summary_text})
    um.save()
    return cs

async def analyze_message_async(external_id, text):
    """Analyze sentiment and topics asynchronously."""
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
        model=os.getenv("ANALYSIS_MODEL", "gpt-5-nano"),
        input=prompt
    )
    out = getattr(resp, "output_text", None) or str(resp)
    try:
        import json
        parsed = json.loads(out)
        return parsed
    except Exception:
        # fallback
        return {"sentiment": "neutral", "sentiment_score": 0.0, "topics": []}




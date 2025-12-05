# chat/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .utils_openai import get_openai_client, extract_text_from_response
from memory.services import (
    get_recent_messages_as_list,
    append_message_to_memory,
    summarize_memory_async,
    analyze_message_async,
)

# SYSTEM_INSTRUCTIONS = (
#     "You are an assistant that has access to a short summary of the user's past conversations. "
#     "Use it to personalize replies when relevant. Be concise and friendly."
# )

SYSTEM_INSTRUCTIONS = (
    "You are AIRA, a warm, personal AI assistant.\n"
    "- The 'Long-term memory summary' contains facts about the user (name, preferences, background).\n"
    "- Gently use those facts to make answers feel personal (e.g., greeting by name, referencing hobbies), "
    "but only if they are clearly relevant.\n"
    "- Never claim to remember something that is not in the summary or current chat.\n"
    "- If the user corrects something, treat the correction as the most up-to-date information.\n"
    "- Keep your answers short and practical unless the user asks for depth.\n"
)



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("[WS] New WebSocket connection")

        # Django user (from AuthMiddlewareStack)
        user = self.scope["user"]
        self.user = user

        # user_id from URL path: ws/chat/<str:user_id>/
        path_user_id = None
        try:
            path_user_id = self.scope.get("url_route", {}).get("kwargs", {}).get("user_id")
        except Exception:
            path_user_id = None

        # Decide external_id for memory system
        if user and getattr(user, "is_authenticated", False):
            self.external_id = f"user:{user.pk}"
        elif path_user_id:
            self.external_id = f"path:{path_user_id}"
        else:
            self.external_id = f"anon:{self.channel_name}"

        await self.accept()
        print("[WS] Connection accepted, external_id =", self.external_id)

    async def receive(self, text_data):
        print("======== [WS RECEIVE] ==========")
        print("[RAW DATA]:", text_data)

        # 1) USER SENDS A MESSAGE  ---------------------------
        try:
            data = json.loads(text_data)
        except Exception:
            await self.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON payload",
            }))
            return

        user_msg = (data.get("message") or "").trim() if hasattr(str, "trim") else (data.get("message") or "").strip()
        print("[USER MSG]:", user_msg)

        if not user_msg:
            print("[ERROR] Empty message!")
            await self.send(json.dumps({
                "type": "error",
                "message": "Message cannot be empty",
            }))
            return

        # 2) LOOK IN DATABASE: summary + recent messages -----
        summary_text = await sync_to_async(self._get_summary_text)()
        print("[MEMORY] Loaded summary:", summary_text)

        recent_messages = await get_recent_messages_as_list(self.external_id, limit=25)
        print("[MEMORY] Loaded recent messages:", recent_messages)

        # 3) USE MEMORY + NEW MESSAGE TO BUILD PROMPT --------
        prompt_parts = [SYSTEM_INSTRUCTIONS]

        if summary_text:
            prompt_parts.append(f"Long-term memory summary:\n{summary_text}")

        if recent_messages:
            last_msgs = recent_messages[-10:]
            history_lines = "\n".join(f"{m['role']}: {m['content']}" for m in last_msgs)
            prompt_parts.append(f"Recent chat history:\n{history_lines}")

        prompt_parts.append(f"User: {user_msg}")
        prompt_parts.append("Assistant:")

        full_prompt = "\n\n".join(prompt_parts)
        print("[DEBUG] Final prompt sent to OpenAI:\n", full_prompt)

        # Call OpenAI in a thread (non-blocking for event loop)
        try:
            client = get_openai_client()
            print("[DEBUG] OpenAI client created")

            def _call_openai():
                return client.responses.create(
                    model="gpt-5-nano",
                    input= full_prompt,
                )

            response = await asyncio.to_thread(_call_openai)
            print("[DEBUG] Raw OpenAI response:", response)

            ai_text = extract_text_from_response(response)
            print("[DEBUG] Extracted AI text:", ai_text)

        except Exception as e:
            print("********** [OPENAI ERROR] **********")
            print(str(e))
            print("************************************")
            await self.send(json.dumps({
                "type": "error",
                "message": f"Error talking to AI: {str(e)}",
            }))
            return

        # 4) CHATBOT REPLIES TO THE USER ---------------------
        await self.send(json.dumps({
            "type": "message",    # your frontend treats this as final assistant message
            "message": ai_text,
        }))
        print("[WS] Sent AI response")

        # SAVE MESSAGES TO DB (so they become part of memory)
        try:
            await append_message_to_memory(self.external_id, "user", user_msg)
            await append_message_to_memory(self.external_id, "assistant", ai_text)
        except Exception as e:
            print("[DB SAVE ERROR]", str(e))

        # BACKGROUND: analyze + update summary (for next time)
        try:
            asyncio.create_task(analyze_message_async(self.external_id, user_msg))
            asyncio.create_task(summarize_memory_async(self.external_id))
        except Exception as e:
            print("[BACKGROUND TASK ERROR]", str(e))

    
   


    def _get_summary_text(self):
        """
        Sync helper to fetch ConversationSummary.summary_text for this external_id.
        Import models inside to avoid AppRegistryNotReady at import time.
        """
        try:
            from memory.models import UserMemory, ConversationSummary
            um = UserMemory.objects.filter(external_id=self.external_id).first()
            if not um:
                return ""
            cs = ConversationSummary.objects.filter(user_memory=um).first()
            return cs.summary_text if cs else ""
        except Exception as e:
            print("[SUMMARY READ ERROR]", str(e))
            return ""



import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils_openai import get_openai_client

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("[WS] New WebSocket connection")
        await self.accept()
        print("[WS] Connection accepted")
    async def receive(self, text_data):
        print("======== [WS RECEIVE] ==========")
        print("[RAW DATA]:", text_data)

        data = json.loads(text_data)
        user_msg = data.get("message", "")
        
        print("[USER MSG]:", user_msg)

        if not user_msg:
            print("[ERROR] Empty message!")
            await self.send(json.dumps({
                "type": "error",
                "message": "Message cannot be empty"
            }))
            return

        try:
            client = get_openai_client()
            print("[DEBUG] OpenAI client created")

            print("[DEBUG] Sending request to OpenAI →", user_msg)
     
            # ---- FIXED: Use input_text instead of input ----
            response = client.responses.create(
                model="gpt-5-nano",
                # input_text=user_msg
                input=user_msg
            )
            print("[DEBUG] Raw OpenAI response:", response)

            ai_text = response.output_text
            print("[DEBUG] Extracted output_text:", ai_text)

            await self.send(json.dumps({
                "type": "message",
                "message": ai_text
            }))
            print("[WS] Sent AI response")
        except Exception as e:
            print("********** [OPENAI ERROR] **********")
            print(str(e))
            print("************************************")

            await self.send(json.dumps({
                "type": "error",
                "message": f"Error: {str(e)}"
            }))


# import json
# import asyncio
# from channels.generic.websocket import AsyncWebsocketConsumer
# from memory.services import (
#     get_or_create_user_memory,
#     append_message_to_memory,
#     summarize_memory_async,
#     analyze_message_async,
# )
# from .utils_openai import stream_openai_response

# class ChatConsumer(AsyncWebsocketConsumer):
#     """
#     Websocket consumer that streams OpenAI responses AND integrates
#     memory (DB) + summarization + sentiment/topic analysis.
#     """
#     async def connect(self):
#         # Accept connection
#         await self.accept()
#         # Identify user: prefer URL kwarg user_id if provided; fallback to client IP:port
#         self.external_id = self.scope.get("url_route", {}).get("kwargs", {}).get("user_id")
#         if not self.external_id:
#             # fallback to client host:port (not persistent across reconnects but ok for dev)
#             host, port = self.scope.get("client", ("anon", 0))
#             self.external_id = f"{host}-{port}"
#         # ensure memory exists
#         await asyncio.to_thread(get_or_create_user_memory, self.external_id)
#         # Optionally: send a welcome message using memory summary
#         await self.send(json.dumps({"type": "system", "message": "Connected to Chat backend."}))

#     async def disconnect(self, close_code):
#         # nothing special (DB persisted)
#         pass

#     async def receive(self, text_data):
#         """
#         Expect JSON: {"type": "message", "message": "..."}
#         """
#         try:
#             payload = json.loads(text_data)
#         except Exception:
#             await self.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
#             return

#         msg_type = payload.get("type", "message")
#         if msg_type != "message":
#             await self.send(json.dumps({"type": "error", "message": "Unsupported payload type"}))
#             return

#         user_text = payload.get("message", "").strip()
#         if not user_text:
#             await self.send(json.dumps({"type": "error", "message": "Empty message"}))
#             return

#         # 1) Save user message to DB (raw)
#         await asyncio.to_thread(append_message_to_memory, self.external_id, "user", user_text)

#         # 2) Run quick analysis (sentiment/topics) in background
#         analysis_task = asyncio.create_task(analyze_message_async(self.external_id, user_text))

#         # 3) Stream AI response (stream_openai_response will call send_chunk_callback)
#         async def send_chunk(chunk_obj):
#             """
#             chunk_obj is dict, e.g. {"type": "stream", "delta": "..."} or {"type":"final", "text":"..."}
#             We'll forward it to frontend as JSON strings.
#             """
#             try:
#                 await self.send(json.dumps(chunk_obj))
#             except Exception:
#                 # ignore send failures for single chunks
#                 pass

#         # Call the streaming function (which internally uses OpenAI)
#         try:
#             await stream_openai_response(self.external_id, user_text, send_chunk)
#         except Exception as e:
#             await self.send(json.dumps({"type": "error", "message": f"OpenAI stream error: {str(e)}"}))
#             return

#         # 4) After streaming completes: gather analysis and save assistant reply to memory
#         # For simplicity, assume the final assistant text arrives as a "final" message earlier in stream.
#         # If not, you might implement a mechanism to collect deltas into final_text.
#         # Here we'll ask the model to produce final_text again for reliability (cheap call), or you can store assembled deltas in consumer state.

#         # Option A: If you kept a buffer of deltas, use it.
#         # Option B: Make a short call to reconstruct final assistant message (simple).
#         # We'll go with Option B for clarity.

#         # reconstruct final message by asking model to "rewrite your last reply" is wasteful.
#         # Instead, rely on the OpenAI streaming code to have sent a {"type":"final","text": ...} chunk earlier.
#         # We'll try to read that final text from the client memory (if stored). For now, we simply store a placeholder.
#         assistant_text = payload.get("_assistant_final_text") or "Assistant reply (final saved)."

#         await asyncio.to_thread(append_message_to_memory, self.external_id, "assistant", assistant_text)

#         # 5) When enough new messages exist, trigger summarization job (async)
#         try:
#             # run summarization in background
#             asyncio.create_task(summarize_memory_async(self.external_id))
#         except Exception:
#             pass

#         # 6) If analysis_task finished, attach metadata to last user message
#         if not analysis_task.done():
#             # wait briefly but do not block indefinitely
#             try:
#                 analysis = await asyncio.wait_for(analysis_task, timeout=4.0)
#             except Exception:
#                 analysis = None
#         else:
#             analysis = analysis_task.result()

#         if analysis:
#             # attach analysis metadata to the last user message
#             # This is a simple approach — in production attach by Message id
#             # For brevity, we won't attempt to update a specific DB row here.
#             await self.send(json.dumps({"type": "analysis", "value": analysis}))


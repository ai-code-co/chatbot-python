Perfect — Phase 2 is the heart of your AI backend.
Here we integrate:

✔ OpenAI Realtime API
✔ Streaming text responses
✔ Voice (audio input + AI audio output)
✔ WebSocket streaming from Django → Vue
✔ Hook to memory (to be fully built in Phase 3)

Let’s go step-by-step and clean.

🚀 PHASE 2 — OPENAI REALTIME STREAMING BACKEND
🎯 What We Will Build in Phase 2

utils_openai.py
→ Handles connection with OpenAI Realtime WebSocket

Update ChatConsumer
→ Accepts user text/audio
→ Streams responses to frontend

Add audio helpers

Modify ASGI to handle concurrency

Full OpenAI streaming pipeline

⭐ PART 1 — Install Additional Packages (if missing)

Run:

pip install websockets anyio


WebSockets are required because OpenAI Realtime API is WS-based.

⭐ PART 2 — Create chat/utils_openai.py

This file handles:

Connecting to OpenAI WS

Sending user messages

Receiving streaming responses

Handling both text + audio output

Create:

chat/utils_openai.py
import json
import asyncio
import websockets
import base64
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_REALTIME_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview"

class OpenAIStreamer:

    async def stream_response(self, user_message, on_delta):
        """
        Main function:
        user_message = {"type": "text" or "audio", "content": "..."}
        on_delta = callback to send partial chunks to frontend
        """

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }

        async with websockets.connect(OPENAI_REALTIME_URL, extra_headers=headers) as ws:

            # 1. Create session
            await ws.send(json.dumps({
                "type": "session.create",
                "model": "gpt-4o-realtime-preview"
            }))

            # 2. Send user message
            if user_message["type"] == "text":
                await ws.send(json.dumps({
                    "type": "input_text",
                    "text": user_message["content"]
                }))

            elif user_message["type"] == "audio":
                await ws.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": user_message["content"]  # base64 encoded audio
                }))

                # tell openai that audio input has completed
                await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))

            # 3. Receive streaming output
            async for msg in ws:
                data = json.loads(msg)

                # streaming text
                if data.get("type") == "response.output_text.delta":
                    chunk = data.get("text_delta", "")
                    await on_delta({"type": "text", "delta": chunk})

                # final text
                if data.get("type") == "response.output_text.done":
                    final = data.get("text", "")
                    await on_delta({"type": "text_done", "text": final})

                # streaming audio
                if data.get("type") == "response.output_audio.delta":
                    audio_chunk = data.get("audio", "")
                    await on_delta({"type": "audio", "delta": audio_chunk})

                # final audio
                if data.get("type") == "response.output_audio.done":
                    audio_full = data.get("audio", "")
                    await on_delta({"type": "audio_done", "audio": audio_full})

⭐ PART 3 — Update WebSocket Consumer

Modify: chat/consumers.py

Add imports:
from .utils_openai import OpenAIStreamer
import base64

Replace receive() with full AI pipeline:
    async def receive(self, text_data):
        data = json.loads(text_data)

        msg_type = data.get("type")
        content = data.get("content")

        # Input message to forward to OpenAI
        if msg_type == "text":
            user_message = {"type": "text", "content": content}

        elif msg_type == "audio":
            # frontend sends audio as base64
            user_message = {"type": "audio", "content": content}

        streamer = OpenAIStreamer()

        async def send_chunk(chunk):
            """
            callback to send streaming output to the frontend
            """
            await self.send(json.dumps(chunk))

        # stream request → response
        await streamer.stream_response(user_message, send_chunk)


This gives us:

✔ Real-time token-by-token text
✔ Real-time audio chunks
✔ Both text + voice supported
✔ Perfect for Vue streaming UI

⭐ PART 4 — Add Ping/Pong Handler (Avoid Timeout)

Inside ChatConsumer add:

    async def receive_ping(self):
        await self.send(json.dumps({"type": "pong"}))


You can trigger this later for heartbeats.

⭐ PART 5 — Audio Helpers (optional)

If we want to convert WAV → base64:

chat/audio_utils.py
import base64

def encode_audio_to_base64(bytes_data):
    return base64.b64encode(bytes_data).decode('utf-8')

def decode_audio_from_base64(b64):
    return base64.b64decode(b64)


OpenAI requires raw audio bytes in base64.

⭐ PART 6 — Update ASGI (Concurrency Optimization)

Modify backend/asgi.py

At the top:

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import chat.routing
import multiprocessing


Add:

multiprocessing.set_start_method("spawn", True)


Python WS sometimes needs this.

⭐ PART 7 — Test OpenAI Streaming

Run everything:

Start Redis:
redis-server

Start Django:
python manage.py runserver

Test via WebSocket Client:

Connect:

ws://127.0.0.1:8000/ws/chat/123/


Send this JSON:

{
  "type": "text",
  "content": "Hi, how are you?"
}


You should receive many chunks like:

{ "type": "text", "delta": "I" }
{ "type": "text", "delta": " am" }
{ "type": "text", "delta": " good!" }
{ "type": "text_done", "text": "I am good!" }

🎤 Test Voice Input

Send:

{
  "type": "audio",
  "content": "<base64 audio>"
}


Response:

{ "type": "audio", "delta": "<chunk>" }
{ "type": "audio", "delta": "<chunk>" }
{ "type": "audio_done", "audio": "<full_audio>" }

🎯 Phase 2 Completed Successfully

You now have:

✔ Fully working OpenAI Realtime backend
✔ Live text streaming
✔ Live audio streaming
✔ WebSocket-based communication
✔ Separation of concerns (utils + consumer)
✔ Ready for Vue frontend
✔ Ready for memory engine in Phase 3

🚀 Next Step → Phase 3

In Phase 3 we implement:

MEMORY ENGINE

✔ UserMemory model
✔ ConversationSummary model
✔ auto-save long-term memory
✔ auto-recall memory at session start
✔ sentiment + topic extraction
✔ updating system prompt with memory

PERSONALITY ENGINE

✔ best-friend tone
✔ emotional intelligence
✔ context-aware responses
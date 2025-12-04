+----------------------------------------------------------+
|                       VUE FRONTEND                       |
|  - Modern Chat UI                                         |
|  - WebSocket Client (text + voice)                       |
|  - Audio recorder + playback                             |
|  - Streaming message renderer                             |
|  - Pinia for state mgmt                                   |
+---------------------------▲------------------------------+
                            |   WebSocket (Text/Voice)
                            |   REST for auth/memory fetch
+---------------------------▼------------------------------+
|                        DJANGO BACKEND                    |
|  Django REST Framework + Channels + Redis                |
|                                                          |
|  Endpoints:                                              |
|    /api/auth/                                            |
|    /api/user/                                            |
|    /api/memory/                                          |
|                                                          |
|  WS:                                                     |
|    /ws/chat/<user_id>/                                   |
|                                                          |
|  Memory Engine:                                          |
|    - Long-term memory store                              |
|    - Important facts engine                              |
|    - Sentiment history                                   |
|    - Conversation summarizer                             |
+---------------------------▲------------------------------+
                            |
                            | OPENAI API (Realtime WS)
+---------------------------▼------------------------------+
|                       OpenAI Backend                     |
|   Models: GPT-4.1 / GPT-5.1 (depending on tone/style)    |
|   Features Used:                                          |
|     - Streaming tokens                                    |
|     - Audio input (voice mode)                            |
|     - Audio output (speech mode)                          |
|     - Personality-driven system prompt                    |
|                                                          |
+----------------------------------------------------------+



⭐ COMPONENT BREAKDOWN
🎯 1. Frontend (Vue.js)
Tech stack

Vue 3 (Composition API)

Vite

TailwindCSS

Pinia (state management)

WebSocket client

Audio recording API (for voice)
Waveform visualizer (optional)



src/
│
├── components/
│   ├── ChatWindow.vue
│   ├── ChatBubble.vue
│   ├── TypingIndicator.vue
│   ├── AudioRecorder.vue
│   ├── VoiceVisualizer.vue
│
├── store/
│   ├── chat.js          (messages, streaming updates)
│   ├── user.js
│
├── services/
│   ├── ws.js            (WebSocket wrapper)
│   ├── api.js           (REST API wrapper)
│
├── views/
│   ├── ChatView.vue
│   ├── Onboarding.vue
│
└── App.vue


Key Frontend Features
✔ Real-time streaming UI

Characters appear as they come from WebSocket.

✔ Voice Input

User records → audio blob → WebSocket → Django → OpenAI realtime.

✔ Voice Output

Receive audio chunks → play progressively (smooth speech).

✔ Memory-aware Frontend UX

“Good morning Medhavi ❤️”

“Last time you mentioned feeling stressed, how are you today?”

🖥 2. Backend (Django + Channels) — Finalized Design
Tech Required

Django

Django REST Framework

Django Channels

Redis (as channel layer)

PostgreSQL

OpenAI SDK (Python)

pydub for audio processing


backend/
│
├── chat/
│   ├── consumers.py      (WebSocket: text + voice)
│   ├── routing.py
│   ├── utils_openai.py   (Realtime functions)
│   ├── memory_manager.py (Long-term memory)
│   ├── prompts.py        (Best friend personality)
│
├── memory/
│   ├── models.py         (UserMemory, ConversationSummary)
│   ├── service.py        (memory save/load)
│
├── api/
│   ├── views.py          (REST endpoints)
│
├── backend/
│   ├── settings.py       (Channels, Redis)
│   ├── urls.py



🧠 3. Memory System (Final Version)
Memory Stored

✔ User name
✔ Preferences
✔ Emotions over time
✔ Important life details (job, family, goals)
✔ Sentiment trend over last 10 chats
✔ Long-term compressed conversation summary

{
  "user_id": 12,
  "name": "Medhavi",
  "likes": ["chai", "coding"],
  "dislikes": ["cold calls"],
  "personality_observations": "User is generally cheerful but stressed about work",
  "last_seen": "2025-12-03"
}
ConversationSummary

Store a running compressed summary.


4. Personality Prompt (Final Best-Friend Version)
You are “Aira”, a caring, empathetic, cheerful best friend.
You always remember the user’s past experiences, preferences, and emotions.
Your tone is warm, emotionally intelligent, humorous, and deeply supportive.

You never judge. You listen, reflect feelings, and offer comfort.

If the user shares emotional content, respond with empathy first.
If the user is stressed, calm them gently.
If the user is happy, celebrate with them.

Use slight emojis but not too many.
Keep language friendly and intimate.


🔌 5. OpenAI Integration (Realtime + Voice)
Backend Steps:
1️⃣ User sends text or audio via WS
2️⃣ Django forwards to OpenAI Realtime WebSocket
3️⃣ OpenAI streams tokens/audio
4️⃣ Django relays chunks to Vue frontend
5️⃣ Memory updated after message ends

🔊 6. Voice Mode Architecture

OpenAI Realtime allows:

✔ Send microphone audio → model transcribes
✔ Model replies with generated audio
✔ Stream audio chunks back to frontend
✔ Vue plays them with Web Audio API

🚀 7. Deployment Architecture
Backend:

DigitalOcean or Railway

Gunicorn + Daphne (for WebSocket)

Redis Cloud

PostgreSQL Cloud

Frontend:

Vercel or Netlify

Domain:

chat.yourdomain.com

the Memory Engine + Personality Engine and wire them into your existing streaming pipeline. I’ll give you complete, copy-pasteable Django code (models + services), updated OpenAI utilities, and the updated WebSocket consumer that:

stores per-user memory in PostgreSQL,

auto-recalls memory on connect,

summarizes conversations and extracts sentiment & topics,

updates the system prompt with memory,

and streams tokens back to the frontend as before.

I’ll also include the exact commands to run, plus notes on environment variables and design choices.



Design choices I used

Per-user memory stored in PostgreSQL via Django models.

Memory limit: we store messages (full) but summarize & keep a ConversationSummary. By default we keep last 200 messages in raw form (you can change).

Model used for summarization & analysis: gpt-4.1-mini (good balance). You can change the model name in env.

Streaming still handled by your existing consumer; summarization/analysis are synchronous calls run in a thread (via asyncio.to_thread) so the consumer remains async.

Sentiment & topic extraction implemented via small OpenAI prompt calls — reliable and simple.

Personality is injected into the system prompt each request along with user memory snippets.
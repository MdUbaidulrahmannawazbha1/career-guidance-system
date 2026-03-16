"""
AI career-counsellor chatbot.

Wraps the Groq LLM API (llama3-8b-8192) with a fixed system prompt that
positions it as an expert career counsellor for engineering students in India.
Conversation history is threaded through every API call so the model can
refer back to previous messages.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT: str = (
    "You are an expert AI career counsellor helping engineering students in India. "
    "Provide guidance on career paths, skill development, placement preparation. "
    "Be encouraging, specific and practical."
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def chat(message: str, history: List[Dict[str, str]]) -> str:
    """Send a message to the Groq LLM and return the assistant reply.

    Args:
        message: The latest user message.
        history: Previous turns as a list of dicts with ``role`` and
                 ``content`` keys (``user`` / ``assistant``).  The list is
                 in chronological order (oldest first).

    Returns:
        The assistant's reply as a plain string.
    """
    from groq import AsyncGroq  # type: ignore[import-untyped]
    from app.config import settings

    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    # Build the full message list: system + history + current message
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    for turn in history:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})

    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,  # type: ignore[arg-type]
            max_tokens=settings.GROQ_MAX_TOKENS,
            temperature=settings.GROQ_TEMPERATURE,
        )
        reply: str = response.choices[0].message.content or ""
        return reply.strip()
    except Exception as exc:
        logger.error("Groq API call failed: %s", exc)
        raise RuntimeError("Chat service is temporarily unavailable. Please try again later.") from exc

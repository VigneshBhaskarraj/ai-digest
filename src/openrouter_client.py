"""
openrouter_client.py
Thin wrapper around OpenRouter's OpenAI-compatible API.

OpenRouter gives access to 200+ models (Claude, GPT-4, Gemini, Llama, Mistral,
DeepSeek, etc.) through a single endpoint. We use it for the cheap signal
extraction pass — running a fast/affordable model over raw articles before
the expensive Claude synthesis pass.

Requires: OPENROUTER_API_KEY in environment (or .env)
Install:   pip install openai>=1.0.0

Usage:
    from openrouter_client import openrouter_complete, EXTRACTION_MODEL

    response = openrouter_complete(
        model=EXTRACTION_MODEL,
        system="You are a signal extractor...",
        user="Articles: ...",
        max_tokens=2000,
    )
    # response is a plain string (the model's reply)
"""

import os
from typing import Optional

# Lazy import — only needed if OpenRouter is configured
try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# The model used for the cheap extraction pass.
# Options ranked by cost/quality tradeoff for structured extraction:
#   "google/gemini-flash-1.5"      — very cheap, fast, good JSON
#   "mistralai/mistral-7b-instruct" — ultra-cheap, decent extraction
#   "meta-llama/llama-3-8b-instruct" — free tier available
#   "anthropic/claude-haiku-4-5"   — slightly pricier but very reliable JSON
EXTRACTION_MODEL = os.environ.get(
    "OPENROUTER_EXTRACTION_MODEL",
    "google/gemini-flash-1.5"
)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
SITE_URL = "https://vigneshbhaskarraj.github.io/ai-digest"
SITE_NAME = "AI Digest"


def _get_client() -> "OpenAI":
    if not _OPENAI_AVAILABLE:
        raise ImportError(
            "openai package not installed. Run: pip install openai>=1.0.0"
        )
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not set. Add it to .env or GitHub Actions secrets."
        )
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
        },
    )


def openrouter_complete(
    user: str,
    system: str = "",
    model: str = "",
    max_tokens: int = 2000,
    temperature: float = 0.2,
) -> str:
    """
    Call OpenRouter with a system + user message pair.
    Returns the raw text content of the first choice.

    Args:
        user:        The user message (article text, prompt, etc.)
        system:      Optional system prompt
        model:       OpenRouter model string (defaults to EXTRACTION_MODEL)
        max_tokens:  Max tokens in response
        temperature: Sampling temperature (low = more deterministic JSON)

    Returns:
        str: Model response text, or empty string on failure
    """
    client = _get_client()
    model = model or EXTRACTION_MODEL

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        print(f"[OpenRouter] Request failed for model {model}: {exc}")
        return ""


def is_available() -> bool:
    """Returns True if OpenRouter is configured and openai package is installed."""
    return bool(OPENROUTER_API_KEY) and _OPENAI_AVAILABLE


if __name__ == "__main__":
    if not is_available():
        print("OpenRouter not configured — set OPENROUTER_API_KEY and install openai")
    else:
        print(f"OpenRouter ready. Extraction model: {EXTRACTION_MODEL}")
        result = openrouter_complete(
            system="You are a concise assistant.",
            user="Say hello in exactly 5 words.",
            max_tokens=50,
        )
        print(f"Test response: {result}")

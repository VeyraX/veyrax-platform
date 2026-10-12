"""LLM access for the backend. Every model call goes through OpenRouter, so OPENROUTER_API_KEY is the only key needed.

Model IDs: https://openrouter.ai/models. The agent and fast models can be overridden with OPENROUTER_AGENT_MODEL and
OPENROUTER_FAST_MODEL (e.g. to use a cheaper or a ":free" model).
"""
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

# main.py imports most modules before it calls load_dotenv(), so load .env here for the model overrides below
load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Tool-using agents: flow runs, MCP Dockerfile and metadata generation
AGENT_MODEL = os.getenv("OPENROUTER_AGENT_MODEL") or "anthropic/claude-sonnet-5.5"
# Short structured tasks: tool parameter generation, data extraction, display names
FAST_MODEL = os.getenv("OPENROUTER_FAST_MODEL") or "openai/gpt-6-luna"
# Web research agent of the lead enrichment feature (fild)
RESEARCH_MODEL = "google/gemini-3.8-flash"
# Same vectors as OpenAI's text-embedding-3-small (1536 dimensions), so existing vector indexes stay valid
EMBEDDING_MODEL = "openai/text-embedding-3-small"


def openrouter_client_kwargs() -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")
    return {
        "api_key": api_key,
        "base_url": OPENROUTER_BASE_URL,
        "default_headers": {
            "HTTP-Referer": os.getenv("SITE_URL") or "https://veyraxapp.com",
            "X-Title": os.getenv("SITE_NAME") or "Veyrax",
        },
    }


def openrouter_client() -> OpenAI:
    return OpenAI(**openrouter_client_kwargs())


def async_openrouter_client() -> AsyncOpenAI:
    return AsyncOpenAI(**openrouter_client_kwargs())


def embed(text: str) -> list[float]:
    return openrouter_client().embeddings.create(model=EMBEDDING_MODEL, input=text).data[0].embedding


def complete(system_message: str, user_message: str, model: str = FAST_MODEL) -> str:
    response = openrouter_client().chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_message}],
    )
    return response.choices[0].message.content


def use_openrouter_for_agents() -> AsyncOpenAI:
    """Point the OpenAI Agents SDK at OpenRouter. Tracing is off: the SDK would export traces to OpenAI."""
    from agents import set_default_openai_api, set_default_openai_client, set_tracing_disabled

    client = async_openrouter_client()
    set_tracing_disabled(True)
    set_default_openai_api("chat_completions")
    set_default_openai_client(client, use_for_tracing=False)
    return client

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

# Disable tracing (requires OpenAI API key we don't have)
set_tracing_disabled(True)

# Ollama local server configuration
BASE_URL = "http://localhost:11434/v1"
MODEL_NAME = "qwen3.5:4b"

# Dedicated classifier model for input guardrails.
# Gemma3 1B: tiny, fast, no thinking mode. Pull with: ollama pull gemma3:1b
CLASSIFIER_MODEL = "gemma3:1b"


def get_model() -> OpenAIChatCompletionsModel:
    """Create an OpenAI-compatible model pointing to local Ollama server."""
    client = AsyncOpenAI(base_url=BASE_URL, api_key="ollama")
    return OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)

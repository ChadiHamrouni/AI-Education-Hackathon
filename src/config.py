from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

# Disable tracing (requires OpenAI API key we don't have)
set_tracing_disabled(True)

# Ollama local server configuration
BASE_URL = "http://localhost:11434/v1"
MODEL_NAME = "qwen3.5:4b"

# Dedicated classifier model for guardrails — smaller and faster.
# Pull with: ollama pull llama3.2
CLASSIFIER_MODEL = "llama3.2:latest"

_client = AsyncOpenAI(base_url=BASE_URL, api_key="ollama")

# Ready-to-use model instances — pass directly into Agent(model=...)
main_model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=_client)
classifier_model = OpenAIChatCompletionsModel(model=CLASSIFIER_MODEL, openai_client=_client)

# Temperature settings
# Classifiers need deterministic YES/NO answers — use 0.
# Main agents can be slightly creative in explanations — use 0.2.
CLASSIFIER_TEMPERATURE = 0.0
AGENT_TEMPERATURE = 0.6
 
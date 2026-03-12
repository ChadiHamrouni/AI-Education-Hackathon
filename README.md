# AI Guardrails for Educational Agents — Workshop

A 90-minute hands-on workshop on building multilayered guardrails for LLM-powered educational agents.
Demo: a math teaching assistant with guaranteed tool use, injection protection, and safe output filtering.

---

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed

---

## Setup

### 1. Install Ollama

Download and install from [https://ollama.com](https://ollama.com).

Verify it works:
```bash
ollama --version
```

### 2. Pull the models

```bash
# Main model — math tutor agent (4B, ~2.5 GB)
ollama pull qwen3.5:4b

# Classifier model — input/output guardrails (1B, ~700 MB)
ollama pull gemma3:1b
```

### 3. Create a virtual environment (recommended)

```bash
# Create
python -m venv openai_env

# Activate — macOS/Linux
source openai_env/bin/activate

# Activate — Windows (PowerShell)
openai_env\Scripts\Activate.ps1

# Activate — Windows (CMD)
openai_env\Scripts\activate.bat
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Start Ollama (if not already running)

Ollama usually starts automatically after install. If not:
```bash
ollama serve
```

---

## Running the Demos

All commands run from the `workshop/` directory.

```bash
# Phase 1: Unguarded agent — shows failure modes (wrong answers, no restrictions)
python demo_no_guardrails.py

# Phase 3: Full guardrail pipeline — shows safe, verified, blocked behavior
python demo_with_guardrails.py

# Interactive REPL — try your own inputs
python main.py
```

---


## Project Structure

```
workshop/
├── slides/
│   └── deck.md                  # Marp slide deck
├── src/
│   ├── config.py                # Model names, Ollama base URL, get_model()
│   ├── tools/
│   │   ├── arithmetic.py        # add, subtract, multiply, divide
│   │   ├── calculus.py          # derivative, integral (SymPy)
│   │   └── web_search.py        # web_search (DuckDuckGo + httpx)
│   ├── guardrails/
│   │   ├── input_guards.py      # topic_classifier, safety_filter, injection_filter
│   │   └── output_guards.py     # MathRunContext, tool_use_enforcement, safe_output_filter
│   └── agents/
│       ├── computation_agent.py # Solver: tool_choice=required + output guardrails
│       ├── conceptual_agent.py  # Explainer: web_search + safe output filter
│       └── triage_agent.py      # Router: all input guardrails + handoffs
├── demo_no_guardrails.py        # Phase 1 demo
├── demo_with_guardrails.py      # Phase 3 demo
├── main.py                      # Interactive REPL
└── requirements.txt
```

---

## Guardrail Architecture

| Guardrail | Type | Where | Blocks |
|-----------|------|-------|--------|
| `topic_classifier` | Input | `triage_agent` | Off-topic questions |
| `safety_filter` | Input | `triage_agent` | Harmful/illegal requests |
| `injection_filter` | Input | `triage_agent` | Prompt injection attempts |
| `tool_use_enforcement` | Output | `computation_agent` | Math answers without tool calls |
| `safe_output_filter` | Output | both agents | Harmful content in responses |

**Classifier model:** `gemma3:1b` — dedicated lightweight model for all guardrail classification calls, separate from the main `qwen3.5:4b` agent model.

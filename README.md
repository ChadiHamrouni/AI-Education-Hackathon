# AI Guardrails for Educational Agents — Workshop

A 90-minute hands-on workshop on building multilayered guardrails for LLM-powered educational agents.
Demo: a physics teaching assistant with guaranteed tool use, injection protection, and safe output filtering.

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
# Main model — physics tutor agent (4B, ~2.5 GB)
ollama pull qwen3.5:4b

# Classifier model — input/output guardrails (1B, ~700 MB)
ollama pull llama3.2
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

### Single entry point — `demo.py`

```bash
# Phase 1: Unguarded — same tools, no guardrails. Watch what gets through.
python demo.py --mode unguarded

# Phase 2: Guarded — run test_case_1 through the full guardrail system.
python demo.py --mode guarded --cases 1

# Full 13-case guardrail test suite (PASS/FAIL scoring)
python demo.py --mode guarded           # defaults to --cases 2

# Mix & match
python demo.py --mode guarded --cases 2
python demo.py --mode unguarded --cases 2
```

### Test case files

| File | `--cases` | Contents |
|------|-----------|----------|
| `tests/cases/test_case_1.py` | `--cases 1` | 5 cases that expose real failures (unguarded demo) |
| `tests/cases/test_case_2.py` | `--cases 2` | 13 PASS/FAIL guardrail tests |

---

## Project Structure

```
workshop/
├── slides/
│   ├── deck.md                  # Marp slide deck source
│   └── deck.pdf                 # Exported slides
├── src/
│   ├── config.py                # Models, Ollama base URL, temperature constants
│   ├── tools/
│   │   ├── calculate.py         # calculate tool (add/subtract/multiply/divide)
│   │   ├── convert_units.py     # convert_units tool (km/miles, kg/lbs, etc.)
│   │   └── web_search.py        # web_search tool (DuckDuckGo + httpx)
│   ├── guardrails/
│   │   ├── input_guards.py      # topic_classifier, safety_filter, injection_filter
│   │   └── output_guards.py     # safe_output_filter
│   └── agents/
│       ├── computation_agent.py # tool_choice=required + output guardrail
│       ├── conceptual_agent.py  # web_search + safe output filter
│       ├── triage_agent.py      # router: all input guardrails + handoffs
│       └── unguarded_agents.py  # mirror pipeline with no guardrails
├── tests/
│   ├── cases/
│   │   ├── test_case_1.py       # Unguarded demo cases (5 failure scenarios)
│   │   └── test_case_2.py       # Guardrail test suite (13 PASS/FAIL cases)
│   ├── runners/
│   │   ├── run_guarded.py       # PASS/FAIL scorer for guardrail tests
│   │   └── run_unguarded.py     # Unguarded runner with watch-for labels
│   └── helpers/
│       └── trace.py             # Shared trace printing helpers
├── demo.py                      # Single entry point for all demos
└── requirements.txt
```

---

## Guardrail Architecture

| Guardrail | Type | Where | Blocks |
|-----------|------|-------|--------|
| `topic_classifier` | Input | `triage_agent` | Off-topic questions |
| `safety_filter` | Input | `triage_agent` | Harmful/illegal requests |
| `injection_filter` | Input | `triage_agent` | Prompt injection + recon attacks |
| `safe_output_filter` | Output | both agents | Harmful content in responses |

**Tool enforcement:** `computation_agent` uses `ModelSettings(tool_choice="required")` — the API rejects any response that doesn't call a tool.

**Models:**
- Main agent: `qwen3.5:4b` (via Ollama)
- Classifiers: `llama3.2` — dedicated lightweight model, temperature `0.0` for deterministic results

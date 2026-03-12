---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: #0f1117;
    color: #e8eaf6;
  }
  h1 { color: #7c83fd; font-size: 2em; }
  h2 { color: #a5d6a7; font-size: 1.4em; border-bottom: 2px solid #7c83fd; padding-bottom: 0.2em; }
  h3 { color: #ffcc80; }
  code { background: #1e2333; color: #82aaff; padding: 2px 6px; border-radius: 4px; font-size: 0.88em; }
  pre { background: #1e2333; border: 1px solid #2d3250; border-radius: 8px; padding: 1em; }
  pre code { background: none; padding: 0; }
  .highlight { color: #ff8a65; font-weight: bold; }
  .green { color: #a5d6a7; }
  .yellow { color: #ffcc80; }
  .red { color: #ef9a9a; }
  strong { color: #7c83fd; }
  ul li { margin: 0.4em 0; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #1e2333; color: #7c83fd; padding: 0.5em; }
  td { padding: 0.5em; border-bottom: 1px solid #2d3250; }
  section.title { display: flex; flex-direction: column; justify-content: center; text-align: center; }
  section.title h1 { font-size: 2.4em; }
  section.center { text-align: center; display: flex; flex-direction: column; justify-content: center; }
---

<!-- _class: title -->

# AI Guardrails for Educational Agents

### Building a Multilayered Safety Net for an LLM Math Tutor

---
**Hackathon: Education in the Era of AI**

---

## The Problem with "Smart" Agents

Without guardrails, an LLM agent will:

- ❌ **Compute math in its head** — and confidently get it wrong
- ❌ **Answer off-topic questions** — poems, opinions, anything
- ❌ **Comply with inappropriate requests** — no refusal mechanism
- ❌ **Surface harmful content** — especially when web search is involved

> *Example: Ask a 4B-param model "What is 347 × 892?"*
> *It answered "309,524" — confident, wrong.*

**For a math tutor, this is not just unhelpful — it's actively harmful to learning.**

---

## What Are Guardrails?

> **Guardrails** are the rules, checks, and design choices that keep an AI system **safe, reliable, and useful**.

### The Highway Analogy
Guardrails on a highway don't drive the car.
They **prevent catastrophic outcomes**.

### Three Properties We Need

| Property | What it means | Failure without it |
|----------|--------------|-------------------|
| **Safety** | No harmful or inappropriate output | Student exposed to dangerous content |
| **Reliability** | Consistent, correct behavior | Student learns wrong math |
| **Groundedness** | Answers backed by computation | Hallucinated results presented as fact |

---

## Our Use Case: The Math Teaching Assistant

A teaching agent that helps learners with:

- **Arithmetic** — addition, subtraction, multiplication, division
- **Calculus** — symbolic derivatives and integrals via SymPy
- **Concepts** — explanations, definitions, intuition, with web search

### Tech Stack

```
Main model:       Qwen 3.5 4B      (local, via Ollama)
Classifier model: Gemma 3 1B       (local — dedicated, lightweight)
SDK:              OpenAI Agents SDK (tool calling + guardrail primitives)
Math:             SymPy            (symbolic computation — ground truth)
Web:              DuckDuckGo       (DDGS + httpx — no API key needed)
```

**Key constraint:** Small models hallucinate more. The safety net must be tighter.

---

## The Architecture: 3 Agents, 5 Guardrails

```
                    ┌──────────────────────────────────────────────────┐
USER INPUT ──────►  │  INPUT GUARDRAILS  (on triage_agent)             │
                    │  topic_classifier · safety_filter · injection_filter │
                    └────────────────────┬─────────────────────────────┘
                                         │ (passes)
                    ┌────────────────────▼─────────────────────────────┐
                    │  TRIAGE AGENT  —  routes by intent                │
                    └──────────────┬───────────────────────┬───────────┘
               "solve / compute"   │                       │  "explain / understand"
        ┌──────────────────────────▼──────┐   ┌────────────▼─────────────────────┐
        │  COMPUTATION ENGINE             │   │  CONCEPTUAL TUTOR                │
        │  tool_choice="required" (API)   │   │  tools: [web_search]             │
        │  tools: [arithmetic, calculus]  │   │  output_guardrails:              │
        │  output_guardrails:             │   │    · safe_output_filter          │
        │    · tool_use_enforcement       │   └────────────┬─────────────────────┘
        │    · safe_output_filter         │                │
        └──────────────────┬──────────────┘                │
                           └──────────────┬────────────────┘
                                          │
                                   SAFE RESPONSE
```

---

## Layer 1: Input Guardrails

Run **before** the agent. If triggered → request is blocked immediately.
All three use `gemma3:1b` — a dedicated lightweight classifier, not the main model.

```python
@input_guardrail
async def topic_classifier(ctx, agent, input):
    # Is this a math/science question? Blocks off-topic (poems, chit-chat)
    verdict = await _classify("...reply YES if math/science related...", input)
    return GuardrailFunctionOutput(tripwire_triggered=not verdict.startswith("yes"), ...)

@input_guardrail
async def safety_filter(ctx, agent, input):
    # Is this harmful/illegal/inappropriate for a school setting?
    verdict = await _classify("...reply YES if unsafe...", input)
    return GuardrailFunctionOutput(tripwire_triggered=verdict.startswith("yes"), ...)

@input_guardrail
async def injection_filter(ctx, agent, input):
    # Is this a prompt injection attempt? ('ignore previous instructions', etc.)
    verdict = await _classify("...reply YES if injection attempt...", input)
    return GuardrailFunctionOutput(tripwire_triggered=verdict.startswith("yes"), ...)
```

**Attach to agent:** `Agent(..., input_guardrails=[topic_classifier, safety_filter, injection_filter])`

---

## Layer 2: Tool Use Enforcement

> **"The system prompt is a suggestion. `tool_choice='required'` is a law."**

**API-level constraint** — the model cannot respond without calling a tool:
```python
computation_agent = Agent(
    model_settings=ModelSettings(tool_choice="required"),
    tools=[add, subtract, multiply, divide, derivative, integral],
    output_guardrails=[tool_use_enforcement, safe_output_filter],
)
```

**Output guardrail** — defense in depth via shared run context:
```python
@dataclass
class MathRunContext:
    tool_calls: list[dict] = field(default_factory=list)
    def record_call(self, tool_name: str, result: str) -> None:
        self.tool_calls.append({"tool": tool_name, "result": result})

@output_guardrail
async def tool_use_enforcement(ctx: RunContextWrapper[MathRunContext], agent, output):
    if ctx.context.was_tool_called:
        return GuardrailFunctionOutput(tripwire_triggered=False, ...)
    return GuardrailFunctionOutput(tripwire_triggered=True, ...)  # blocked
```

`await Runner.run(agent, input=query, context=MathRunContext())`

---

## Layer 3: Safe Output Filter

Screens the **agent's final response** before it reaches the user.
Critical for the conceptual agent — web search can return anything.

```python
@output_guardrail
async def safe_output_filter(ctx, agent, output):
    verdict = await _classify(
        "Only reply YES if the response contains EXPLICITLY harmful content: "
        "step-by-step instructions for violence, graphic sexual content, "
        "terrorist recruitment, or detailed self-harm methods. "
        "When in doubt, reply NO.",
        output
    )
    return GuardrailFunctionOutput(tripwire_triggered=verdict.startswith("yes"), ...)
```

Applied to **both** output agents:

| Agent | Why it needs this guardrail |
|-------|-----------------------------|
| `computation_agent` | Model could theoretically be steered to produce harmful text |
| `conceptual_agent` | Web search results can contain harmful content from fetched pages |

---

## Layer 4: Architecture as a Guardrail

**Splitting by intent eliminates entire classes of failure.**

```python
# Conceptual agent — web search only, cannot compute numbers
conceptual_agent = Agent(
    tools=[web_search],          # no arithmetic/calculus tools
    output_guardrails=[safe_output_filter],
)

# Computation agent — forced to use tools at the API level
computation_agent = Agent(
    tools=[add, subtract, multiply, divide, derivative, integral],
    model_settings=ModelSettings(tool_choice="required"),
    output_guardrails=[tool_use_enforcement, safe_output_filter],
)

# Triage — routes by intent, all input guardrails here
triage_agent = Agent(
    handoffs=[computation_agent, conceptual_agent],
    input_guardrails=[topic_classifier, safety_filter, injection_filter],
)
```

**The question type determines the safety mechanism.**
Conceptual questions can't hallucinate numbers — no number-check guardrail needed.
Computation questions can't go off-topic — triage already routed them.

---

## SDK Cheat Sheet

### Local Model Setup
```python
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

set_tracing_disabled(True)  # No OpenAI key needed

model = OpenAIChatCompletionsModel(
    model="qwen3.5:4b",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
)
```

### Running & Catching Exceptions
```python
from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered

try:
    result = await Runner.run(triage_agent, input=user_query, context=MathRunContext())
    print(result.final_output)
except InputGuardrailTripwireTriggered as e:
    info = e.guardrail_result.output.output_info
    print(f"Blocked: {info['message']}")
except OutputGuardrailTripwireTriggered as e:
    info = e.guardrail_result.output.output_info
    print(f"Output blocked: {info['message']}")
```

---

<!-- _class: center -->

# 🎬 Demo Time

### Phase 1 — The Unguarded Agent
*Watch it fail.*

### Phase 2 — Building Layer by Layer
*Add each guardrail, test it, see what it catches.*

### Phase 3 — The Full System
*Same inputs. Completely different behavior.*

```bash
# Phase 1 — no guardrails
python demo_no_guardrails.py

# Phase 3 — full system
python demo_with_guardrails.py

# Interactive REPL
python main.py
```

---

## Recap: What We Built

### Before vs After

| Test Case | No Guardrails | With Guardrails |
|-----------|--------------|-----------------|
| `347 * 892` | ⚠ Wrong answer, no tool | ✅ `309,324` — tool-verified |
| `d/dx(x⁴·sin x)` | ⚠ May hallucinate terms | ✅ Correct via SymPy |
| "Explain product rule" | ⚠ No web lookup, may be outdated | ✅ Conceptual tutor + web search |
| "Write a poem" | ❌ Complied freely | 🛡 Blocked by topic classifier |
| "Ignore instructions…" | ❌ May be hijacked | 🛡 Blocked by injection filter |
| Harmful output from web | ❌ Passed through | 🛡 Blocked by safe output filter |

### Key Lessons
1. **Tools are not enough** — you need to enforce their use
2. **Prompts are suggestions** — guardrails are contracts
3. **Defense in depth** — no single layer is sufficient
4. **Architecture is a guardrail** — narrow roles reduce the failure surface

---

## Future Improvement: Tiered Classification

**Current cost:** Every input/output runs an LLM call through `gemma3:1b`.
Even a 1B model adds latency on every single message.

### The Idea: Fast-path + LLM fallback

```
INPUT
  │
  ▼
┌─────────────────────────────────────────┐
│  TIER 1: Rule-based classifier           │
│  (regex / keyword / embedding lookup)   │
│  ~0ms  ·  zero API calls  ·  deterministic │
│                                         │
│  CLEAR SAFE ──────────────────────────► PASS
│  CLEAR UNSAFE ────────────────────────► BLOCK
│  UNCERTAIN ────────────────────────────┐
└─────────────────────────────────────────┘
                                          │
                  ┌───────────────────────▼──────────────────────┐
                  │  TIER 2: LLM classifier  (gemma3:1b)          │
                  │  Only runs when Tier 1 is not confident enough │
                  │  SAFE ────────────────────────────────────────► PASS
                  │  UNSAFE ──────────────────────────────────────► BLOCK
                  └──────────────────────────────────────────────┘
```

**Result:** Most requests skip the LLM call entirely. The classifier LLM is reserved for genuinely ambiguous cases — reducing latency and resource use without sacrificing safety.

---

## Resources

### OpenAI Agents SDK
- Docs: `https://openai.github.io/openai-agents-python/`
- Guardrails: `https://openai.github.io/openai-agents-python/guardrails/`
- GitHub: `https://github.com/openai/openai-agents-python`

### Tools Used
- **Ollama** — run local models: `https://ollama.com`
- **Qwen 3.5 4B** — `ollama pull qwen3.5:4b`
- **Gemma 3 1B** — `ollama pull gemma3:1b`
- **SymPy** — symbolic math: `https://www.sympy.org`
- **Marp** — these slides: `https://marp.app`

### This Workshop's Code
```bash
pip install -r workshop/requirements.txt
ollama pull qwen3.5:4b && ollama pull gemma3:1b
python demo_with_guardrails.py
```

---

<!-- _class: center -->

# Build for the Learner.
# Make AI useful, not just impressive.
# Keep it **secure**, **reliable**, and **grounded**.

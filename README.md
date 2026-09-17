# T.A.O.R---Think-Act-Observe-Repeat
# Track 2 — Build the Brain, Not the Puppet

A small agent framework built from scratch (no LangChain / CrewAI / AutoGen for
the actual loop), plus a real research agent built on top of it that uses three
tools and recovers from a tool failure without crashing.

## Quick start

```bash
pip install -r requirements.txt

# Unit tests — no API key or internet needed, tests the loop itself
pytest -v test_framework.py

# Live demo — needs a real key, hits Wikipedia + DuckDuckGo over the network
export ANTHROPIC_API_KEY=sk-ant-...
python demo.py
```

## Architecture

```
Task
  │
  ▼
Agent.run()  ──────────────────────────────────────────────┐
  │  1. Build prompt = system instructions + scratchpad     │  agent_framework/
  │  2. llm.complete(..., stop_sequences=["Observation:"])  │  framework.py
  │  3. Parse "Thought / Action / Action Input"              │  (the actual
  │  4. If Action == "Final Answer" → return                │   deliverable)
  │  5. Else: look up tool by name, run it                  │
  │  6. Catch any exception → turn into an Observation       │
  │  7. Append Thought/Action/Observation to scratchpad      │
  │  8. Go to 1 (until final answer or max_steps)            │
  └───────────────────────────────────────────────────────────┘
        │                              │
        ▼                              ▼
  agent_framework/llm.py         tools/*.py
  (plain HTTP call, no           calculator, wiki_lookup,
   framework logic here)         web_search, flaky_status_api
```

**Files:**
- `agent_framework/framework.py` — the plan→act→observe→repeat loop, prompt
  template, parsing, and error handling. This is the core deliverable.
- `agent_framework/llm.py` — a plain HTTP wrapper around the Anthropic
  Messages API (`AnthropicLLM`), plus a `MockLLM` used only for tests.
- `tools/` — `CalculatorTool` (AST-based, no `eval()`), `WikiLookupTool`
  (Wikipedia REST API), `WebSearchTool` (DuckDuckGo HTML endpoint, no key
  needed), `UnstableAPITool` (deliberately flaky, see below).
- `demo.py` — runs the agent live against real tools.
- `test_framework.py` — 10 tests covering the loop itself with a scripted
  `MockLLM`, so control flow is verified independent of any live model.

## Rule-by-rule compliance

| Rule | How it's met |
|---|---|
| Core loop written by your team, not imported | `framework.py`'s `Agent.run()` / `_parse()` / `_execute_tool()` contain the entire plan-act-observe-repeat logic. The only external call in the loop is `llm.complete()`, a raw HTTP POST — see the docstring at the top of `llm.py`. |
| LangChain-like libs only for small utilities | Not used at all here — `requests` is the only third-party dependency, used for the LLM HTTP call and the tools. |
| ≥2 tools, chosen by the agent, not hardcoded routing | Four tools are registered (`calculator`, `wiki_lookup`, `web_search`, `flaky_status_api`). `Agent` never reads the task text to pick one — it only reads back whichever tool name the model wrote after `Action:` and looks it up in a dict (`_execute_tool`). `test_model_chooses_between_two_tools_itself` pins this down. |
| Show a failed/unexpected tool call, agent notices and recovers | Any exception from `tool.run()` is caught in `_execute_tool` and turned into `Error: ...`, fed back as the next Observation — never a crash. `UnstableAPITool` fails deterministically on its first call so this is demonstrable on demand; see `test_flaky_tool_recovery_end_to_end` and Task 2 in `demo.py`. Unknown-tool-name and malformed-output cases are handled the same way (`test_unknown_tool_name_recovers_instead_of_crashing`, `test_malformed_model_output_triggers_self_correction`). |
| Bonus: compare against a standard framework | See below. |

## Why a flaky tool is included

Judges pushing on "what happens when a tool call fails" against a *real*
third-party API (Wikipedia/DuckDuckGo) is inherently non-deterministic — it
might just work at demo time. `UnstableAPITool` fails on its first call, every
time, so the recovery behavior can be shown reliably in under 10 seconds
without hoping something breaks on cue.

## Bonus: how this differs from LangChain

This isn't a criticism of LangChain — it's a good tool. The point of this
track is understanding what it's doing for you:

- **Control flow is fully visible.** The whole loop is ~100 lines in one
  function. There's no `AgentExecutor`, no internal callback graph, no need
  to read library source to know what happens when a tool errors — it's the
  `except Exception` block a few lines above where the tool is called.
- **The "agent decides which tool" mechanism is just prompt text + string
  parsing**, not a vendor-specific tool-calling schema. That's also the
  weakness: it's less robust than a model's native structured tool-calling,
  which is precisely why this project handles malformed output as a first-class
  recoverable case (`test_malformed_model_output_triggers_self_correction`)
  instead of assuming the model always cooperates.
- **No hidden retries, no hidden prompt templates.** Everything the model
  sees is in `SYSTEM_TEMPLATE` in `framework.py`, in full.

## Limitations

- `WikiLookupTool` and `WebSearchTool` need outbound internet access at
  runtime; they weren't exercised end-to-end in the environment this was
  built in (network egress there is restricted to package registries), but
  their control flow (raising `ToolError` on bad status codes / empty
  results, being caught by `_execute_tool`) is exercised by the same tested
  path as every other tool.
- `max_steps` is a blunt safety net for runaway loops; a stricter version
  could also cap total tokens/cost per run (natural extension toward Track 1
  if you wanted to combine the two).

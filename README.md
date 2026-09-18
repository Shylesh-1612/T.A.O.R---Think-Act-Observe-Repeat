# NEXUS — Autonomous Research & Decision Agent

**Track 2: "BUILD THE BRAIN, NOT THE PUPPET"**

NEXUS is a custom-built autonomous agent that researches real-world questions, dynamically selects tools, observes their results, adapts when tools fail, verifies information, and produces an evidence-backed final result.

## Why this is an agent
NEXUS implements a true agentic loop from scratch. Instead of hardcoded steps or framework wrappers, it provides a transparent core loop that hands decision-making power to an LLM.

## Architecture

```text
User Objective
      ↓
Build Context (agent/prompts.py)
      ↓
LLM Decision (llm/provider.py)
      ↓
Parse / Validate (agent/parser.py)
      ↓
Tool Registry (tools/registry.py)
      ↓
Tool Execution (agent/dispatcher.py)
      ↓
Observation
      ↓
State Update (agent/state.py)
      ↓
Repeat
      ↓
Final Answer
```

## Features
- **Custom Control Loop:** Our own implementation (DECISION -> ACT -> OBSERVE -> REPEAT).
- **Dynamic Tool Selection:** Tools are registered and their JSON schemas are provided to the LLM. No hardcoded routing.
- **Robust Recovery:** Agent detects and handles malformed LLM outputs, invalid tool calls, API rate limits, tool exceptions, and network failures.
- **Security:** API keys are never logged. The calculator utilizes safe AST parsing rather than `eval()`.
- **Testable:** Built-in Mock LLM mode for deterministic offline testing and demonstration without exposing API keys.

## Installation

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup environment variables:
   Copy `.env.example` to `.env` and set `OPENAI_API_KEY` to run the Real LLM mode.

## Usage

### Run Tests
Tests run completely offline using the Mock LLM.
```bash
python -m pytest
```

### Run Terminal Demo
```bash
python demo/demo.py normal
python demo/demo.py failure
```

### Run Streamlit UI
```bash
streamlit run ui/app.py
```

## Known Limitations
- The Extractor currently simulates data structuring via localized regex rather than a full secondary LLM call to save time and API costs, maintaining loop simplicity.
- The Verifier utilizes basic set overlap logic for demonstration.
- Web search relies on the Wikipedia API rather than a raw duckduckgo scraper to ensure reliable operation without 403 Forbidden errors during demonstrations.

## Future Work
- Implement actual nested utility-LLM calls for Extractor and Verifier tools.
- Introduce memory persistence across multiple objective tasks.
- Implement streaming tokens in the UI for real-time decision visibility.

## Compliance
See `docs/COMPLIANCE.md` and `docs/AUDIT.md` for a full trace of explicit requirements to the code implementation.

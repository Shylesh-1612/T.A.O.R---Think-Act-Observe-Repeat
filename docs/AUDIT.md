# NEXUS Project Technical Audit

## 1. Current Architecture
- Custom agent control loop (`agent/core.py`) implementing `PLAN -> ACT -> OBSERVE -> REPEAT`.
- Tool registry (`tools/registry.py`) enabling dynamic tool discovery.
- Output parser (`agent/parser.py`) enforcing JSON structures.
- LLM abstraction (`llm/base.py`) with both a `MockLLM` and an `OpenAIProvider`.

## 2. What is already working
- Test suite (12/12 passing).
- Safe calculator utilizing Python's AST instead of `eval()`.
- Wikipedia-based web search tool.
- MockLLM with deterministic sequence generation.
- Streamlit UI rendering execution traces.
- Simulated failure recovery through `UnreliableDemoTool`.

## 3. What is genuinely agentic
- The tool dispatching system dynamically injects available tool schemas into the system prompt.
- The `AgentParser` catches schema errors and passes them back to the LLM for self-correction.
- The state object appends observations and feeds them back into the LLM context organically.

## 4. What is currently mocked/hardcoded
- `OpenAIProvider` lacks rigorous exception/timeout handling and strict initialization checks.
- `Extractor` relies on simple keyword matching rather than utilizing an LLM utility or robust NLP logic.
- `Verifier` relies on simple string checks (`len(claim) > 5 and "fake" not in claim.lower()`).
- The `demo/demo.py` script hardcodes the mock responses for the UI instead of a truly dynamic scenario.
- Web search limits results and hardcodes the Wikipedia source query structure, making broader queries difficult.

## 5. Potential hackathon compliance issues
- Non-authentic tool implementation: Extractor and Verifier tools barely perform their function and act more as dummies.
- Tool output formatting lacks a fully uniform `metadata` object across all tools.
- "PLAN/THINK" terminology needs updating to "DECISION" per prompt requirements.
- Final answer quality is not enforced in the agent prompt to include structured sections (Summary, Comparison, Calculations, etc).

## 6. Security issues
- Missing robust rate limiting / max token limits on the `OpenAIProvider`.
- Missing explicit check to ensure API keys are not accidentally logged via standard exception stack traces in `agent/core.py`.
- No explicit HTTP timeout for `httpx` in tools like `Extractor` or `Verifier` if they were to make actual requests.

## 7. Demo weaknesses
- The prompt does not encourage the LLM to write precise search queries (e.g., "Tech events" instead of "upcoming technology events Chennai September 2026").
- The Streamlit UI doesn't clearly display whether it is running in "MOCK MODE" or "REAL LLM MODE".
- The UI exposes too much inner JSON data rather than neatly formatted decision summaries.

## 8. Recommended changes
1. **Refactor `OpenAIProvider`**: Properly enforce `OPENAI_API_KEY` loading, add request timeouts, and gracefully catch `openai.APIConnectionError`, `RateLimitError`, etc.
2. **Update Agent Prompt**: Redefine the system instructions to produce focused web queries, enforce structured final answers (Summary, Comparison, Calculations, Evidence, Uncertainty), and rename "PLAN/THINK" to "DECISION".
3. **Refine Tools**: Give `extractor.py` and `verifier.py` slightly more realistic or explicitly acknowledged implementations (e.g., utilizing the LLM API purely as a utility without disrupting the core loop). Ensure consistent `status`, `data`, and `metadata` returns across all tools.
4. **Update UI**: Clearly distinguish Mock vs. Real mode. Improve trace aesthetics to show succinct DECISIONs without exposing raw chains of thought.
5. **Update Loop Logic**: Refine `agent/core.py` to ensure observations structure strictly aligns with Phase 6 instructions.
6. **Expand Tests**: Add 100% test coverage for the new tool edge cases and provider failures.

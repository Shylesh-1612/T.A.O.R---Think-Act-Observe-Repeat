# NEXUS Compliance Audit

| Requirement | Implementation File | Demonstration / Test |
|-------------|---------------------|----------------------|
| **1. Custom agent loop** | `agent/core.py` | The main execution loop clearly iterates through gathering context, prompting the LLM, parsing actions, executing tools via dispatcher, and appending observations. No LangChain or CrewAI orchestration logic is used here. |
| **2. Plan/Think → Act → Observe → Repeat** | `agent/core.py` | Variables and logging trace map perfectly to DECISION/PLAN, ACT, OBSERVE structure. |
| **3. Dynamic tool selection** | `agent/prompts.py`, `agent/core.py` | The LLM decides solely based on the injected schemas via `registry.get_descriptions()`. |
| **4. At least two tools** | `tools/*.py` | 5 distinct tools implemented: web_search, calculator, extractor, verifier, unreliable_demo_tool. |
| **5. Tool registry** | `tools/registry.py` | Centralized `ToolRegistry` injects available tools into the agent. |
| **6. Failure detection** | `agent/core.py`, `agent/parser.py`, `agent/dispatcher.py` | Network timeouts, syntax errors, and LLM output malformations are caught safely and normalized into standard error structures. |
| **7. Failure recovery** | `agent/core.py`, `tools/unreliable_demo_tool.py` | Error observations are fed back to the LLM. The Demo tool forces 2 distinct failures before a success to prove recovery. Tested in `test_agent_malformed_output` and `test_unreliable_tool_demo_mode_on`. |
| **8. Unexpected output handling** | `agent/parser.py` | Strict JSON schema enforcement converts markdown wraps or plain text garbage into explicit errors for the LLM to self-correct. |
| **9. Loop protection** | `agent/core.py` | Detection of identical serialized action repeats, triggering a specific `repeated_action` warning. Max step constraint enforces termination. |
| **10. Real-world task** | `ui/app.py`, `demo/demo.py` | Researching technology events, calculating costs, structuring extracted data, and verifying the claim. |
| **11. No framework controlling the core agent** | `agent/core.py` | Code audit reveals purely native Python loop structures without any underlying orchestrator. |
| **12. Optional framework comparison** | *Omitted intentionally* | Due to time constraints, maintaining a separate clean loop was prioritized over benchmarking against an external framework. |

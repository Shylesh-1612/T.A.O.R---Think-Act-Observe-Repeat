import streamlit as st
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.mock import MockLLM
from llm.provider import GeminiProvider
from tools.registry import ToolRegistry
from tools.calculator import Calculator
from tools.web_search import WebSearch
from tools.extractor import Extractor
from tools.verifier import Verifier
from tools.unreliable_demo_tool import UnreliableDemoTool
from agent.core import NexusAgent

st.set_page_config(page_title="T.A.O.R", layout="wide")

@st.cache_resource
def get_registry():
    registry = ToolRegistry()
    registry.register(Calculator())
    registry.register(WebSearch())
    registry.register(Extractor())
    registry.register(Verifier())
    registry.register(UnreliableDemoTool())
    return registry

def main():
    st.title("T.A.O.R — Think- Act-Observe-Repeat")
    st.markdown("Track 2 — 'BUILD THE BRAIN, NOT THE PUPPET'")

    with st.sidebar:
        st.header("Configuration")
        api_key_exists = bool(os.getenv("GEMINI_API_KEY"))
        
        if api_key_exists:
            st.success("API Key Found")
            use_mock = st.checkbox("Use Mock LLM (For deterministic testing)", value=False)
        else:
            st.warning("No API Key Found. Defaulting to Mock Mode.")
            use_mock = True

        demo_failure = st.checkbox("Enable Demo Failure Mode", value=False)
        max_steps = st.slider("Max Steps", min_value=3, max_value=20, value=10)
        
        st.header("Available Tools")
        registry = get_registry()
        for t in registry.list_tools():
            st.markdown(f"- **{t}**")

    # MODE INDICATOR
    if use_mock:
        st.info("🟡 MOCK MODE — deterministic testing")
    else:
        st.success("🟢 REAL LLM MODE")

    default_obj = "Research three upcoming technology events in Chennai. Find their dates, locations, registration costs, calculate the total cost for attending each, and verify important information using independent sources."
    objective = st.text_area("Enter your research objective:", value=default_obj)

    if st.button("Run Agent"):
        os.environ["DEMO_FAILURE_MODE"] = str(demo_failure).lower()
        
        if use_mock:
            if demo_failure:
                responses = [
                    json.dumps({"type": "tool_call", "tool": "unreliable_demo_tool", "input": {"query": "test"}, "reason": "Testing unreliable tool."}),
                    json.dumps({"type": "tool_call", "tool": "unreliable_demo_tool", "input": {"query": "test"}, "reason": "Retrying after network failure."}),
                    json.dumps({"type": "tool_call", "tool": "unreliable_demo_tool", "input": {"query": "test"}, "reason": "Retrying after malformed result."}),
                    json.dumps({
                        "type": "final",
                        "answer": "## Summary\nTool finally succeeded after multiple adaptations.\n\n## Comparison\n| Option | Result |\n|---|---|\n| Tool | Success |\n\n## Calculations\nN/A\n\n## Evidence\nSuccessfully received response on 3rd attempt.\n\n## Uncertainty\nNone.",
                        "sources": []
                    })
                ]
            else:
                responses = [
                    json.dumps({"type": "tool_call", "tool": "web_search", "input": {"query": "upcoming technology events Chennai 2026 registration fee"}, "reason": "Searching for specific tech events and costs in Chennai."}),
                    json.dumps({"type": "tool_call", "tool": "extractor", "input": {"text": "Event: Tech Summit Chennai 2026, Cost: $100", "fields": ["Cost"]}, "reason": "Extracting cost from search results."}),
                    json.dumps({"type": "tool_call", "tool": "calculator", "input": {"expression": "100 * 3"}, "reason": "Calculating total cost for 3 events."}),
                    json.dumps({"type": "tool_call", "tool": "verifier", "input": {"claim": "Total cost is 300", "source_text": "Event: Tech Summit Chennai 2026, Cost: $100"}, "reason": "Verifying cost calculations against sources."}),
                    json.dumps({
                        "type": "final",
                        "answer": "## Summary\nFound tech events and verified costs.\n\n## Comparison\n| Option | Date | Location | Cost | Verification |\n|---|---|---|---|---|\n| Tech Summit | 2026 | Chennai | $100 | Verified |\n\n## Calculations\n$100 * 3 = $300\n\n## Evidence\nVerified via Wikipedia and Extractor tools.\n\n## Uncertainty\nNo uncertainty in calculation.",
                        "sources": ["Wikipedia"]
                    })
                ]
            llm = MockLLM(responses)
        else:
            try:
                llm = GeminiProvider()
            except RuntimeError as e:
                st.error(str(e))
                return
            
        agent = NexusAgent(llm, registry, max_steps=max_steps)
        
        with st.spinner("Agent is running..."):
            result = agent.run(objective)
            
        st.header("Execution Trace")
        
        state = result.get("state", {})
        history = state.get("history", [])
        
        step_groups = {}
        for item in history:
            step = item["step"]
            if step not in step_groups:
                step_groups[step] = []
            step_groups[step].append(item)
            
        for step, items in step_groups.items():
            with st.expander(f"Step {step}", expanded=True):
                for item in items:
                    if item["type"] == "action":
                        st.markdown("### 🧠 DECISION")
                        st.info(item["data"].get("reason", "No explicit reason."))
                        st.markdown("### 🛠️ ACT")
                        # Hide the internal json, just show tool and input
                        st.write(f"**Tool:** `{item['data'].get('tool')}`")
                        st.json(item["data"].get("input", {}))
                    elif item["type"] == "observation":
                        st.markdown("### 👁️ OBSERVE")
                        if item["data"].get("status") == "success":
                            st.success("Tool Execution Succeeded.")
                        elif item["data"].get("status") == "warning":
                            st.warning(f"Warning: {item['data'].get('message', 'unknown')}")
                        else:
                            st.error(f"Error: {item['data'].get('error_type', 'unknown')} - {item['data'].get('message', '')}")
                        # Filter out metadata from main display for cleanliness, show data
                        if "data" in item["data"]:
                            st.json(item["data"]["data"])
                        
        st.header("Final Answer")
        if result["status"] == "success":
            st.markdown(result["final_answer"].get("answer", "No answer provided."))
            sources = result["final_answer"].get("sources", [])
            if sources:
                st.markdown("**Sources:**")
                for s in sources:
                    st.markdown(f"- {s}")
        else:
            st.error(f"Agent failed to complete: {result.get('message')}")

if __name__ == "__main__":
    main()

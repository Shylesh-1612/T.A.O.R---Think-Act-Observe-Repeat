import os
import sys
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.mock import MockLLM
from llm.provider import OpenAIProvider
from tools.registry import ToolRegistry
from tools.calculator import Calculator
from tools.web_search import WebSearch
from tools.extractor import Extractor
from tools.verifier import Verifier
from tools.unreliable_demo_tool import UnreliableDemoTool
from agent.core import NexusAgent

def setup_registry():
    registry = ToolRegistry()
    registry.register(Calculator())
    registry.register(WebSearch())
    registry.register(Extractor())
    registry.register(Verifier())
    registry.register(UnreliableDemoTool())
    return registry

def run_demo(mode="normal"):
    print("\n" + "="*50)
    print(" "*15 + "NEXUS AGENT DEMO")
    print("="*50)
    
    registry = setup_registry()
    
    # We will use OpenAI Provider if key exists, else fallback to a descriptive MockLLM
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true" or not os.getenv("OPENAI_API_KEY")
    
    if use_mock:
        print("Running with MOCK LLM (No API key found or forced mock).")
        # Provide some fake responses for a controlled demo
        import json
        if mode == "failure":
            os.environ["DEMO_FAILURE_MODE"] = "true"
            responses = [
                json.dumps({"type": "tool_call", "tool": "unreliable_demo_tool", "input": {"query": "test"}, "reason": "Testing unreliable tool."}),
                json.dumps({"type": "tool_call", "tool": "unreliable_demo_tool", "input": {"query": "test"}, "reason": "Retrying after network failure."}),
                json.dumps({"type": "tool_call", "tool": "unreliable_demo_tool", "input": {"query": "test"}, "reason": "Retrying after malformed result."}),
                json.dumps({"type": "final", "answer": "Tool finally succeeded.", "sources": []})
            ]
            objective = "Show me failure recovery."
        else:
            responses = [
                json.dumps({"type": "tool_call", "tool": "web_search", "input": {"query": "Tech events"}, "reason": "Searching for tech events."}),
                json.dumps({"type": "tool_call", "tool": "calculator", "input": {"expression": "5000 + 2500"}, "reason": "Calculating budget."}),
                json.dumps({"type": "final", "answer": "Found tech events and calculated cost is 7500.", "sources": ["Wikipedia"]})
            ]
            objective = "Research tech events and calculate costs."
            
        llm = MockLLM(responses)
    else:
        print("Running with real OpenAI LLM.")
        llm = OpenAIProvider(model="gpt-4o-mini")
        if mode == "failure":
            os.environ["DEMO_FAILURE_MODE"] = "true"
            objective = "Query the unreliable_demo_tool with the query 'test'. Keep retrying until it works, then tell me the result."
        else:
            os.environ["DEMO_FAILURE_MODE"] = "false"
            objective = "Research three upcoming technology events, calculate if 200 * 50 fits my budget, and verify the cost."
            
    agent = NexusAgent(llm, registry, max_steps=10)
    result = agent.run(objective)
    
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    import pprint
    pprint.pprint(result)
    print("\nDemo finished.")

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
    run_demo(mode)

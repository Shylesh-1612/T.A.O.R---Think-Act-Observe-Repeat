from flask import Flask, render_template, request, jsonify
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

app = Flask(__name__)

def get_registry():
    registry = ToolRegistry()
    registry.register(Calculator())
    registry.register(WebSearch())
    registry.register(Extractor())
    registry.register(Verifier())
    registry.register(UnreliableDemoTool())
    return registry

@app.route('/')
def index():
    api_key_exists = bool(os.getenv("GEMINI_API_KEY"))
    registry = get_registry()
    tools = registry.list_tools()
    return render_template('index.html', api_key_exists=api_key_exists, tools=tools)

@app.route('/run', methods=['POST'])
def run_agent():
    data = request.json
    objective = data.get('objective', '')
    use_mock = data.get('use_mock', True)
    demo_failure = data.get('demo_failure', False)
    max_steps = int(data.get('max_steps', 10))
    
    os.environ["DEMO_FAILURE_MODE"] = str(demo_failure).lower()
    
    registry = get_registry()
    
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
            return jsonify({"status": "error", "message": str(e)})

    agent = NexusAgent(llm, registry, max_steps=max_steps)
    
    try:
        result = agent.run(objective)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

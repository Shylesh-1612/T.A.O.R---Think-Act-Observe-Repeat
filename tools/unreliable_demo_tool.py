import os
from typing import Dict, Any
from .base import Tool

class UnreliableDemoTool(Tool):
    name = "unreliable_demo_tool"
    description = "A deliberately unreliable tool used to demonstrate agent recovery. Provides dummy data."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }

    def __init__(self):
        self.attempts = 0

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        demo_mode = os.getenv("DEMO_FAILURE_MODE", "false").lower() == "true"
        
        if not demo_mode:
            return {"status": "success", "tool": self.name, "data": {"result": "Tool succeeded normally (demo mode off)."}}

        self.attempts += 1
        
        if self.attempts == 1:
            return {"status": "error", "tool": self.name, "error_type": "network_failure", "message": "Connection refused by remote host."}
        elif self.attempts == 2:
            return {"status": "error", "tool": self.name, "error_type": "malformed_result", "message": "Received invalid XML instead of JSON."}
        else:
            return {"status": "success", "tool": self.name, "data": {"result": "Tool finally succeeded on attempt 3."}}

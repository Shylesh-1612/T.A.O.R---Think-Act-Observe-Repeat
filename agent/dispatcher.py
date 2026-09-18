import time
from typing import Dict, Any
from tools.registry import ToolRegistry

class ToolDispatcher:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def dispatch(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        try:
            tool = self.registry.get(tool_name)
        except KeyError:
            return {
                "status": "error",
                "error_type": "unknown_tool",
                "requested_tool": tool_name,
                "message": f"Tool '{tool_name}' not found. Available tools: {', '.join(self.registry.list_tools())}"
            }

        try:
            result = tool.run(input_data)
        except Exception as e:
            result = {
                "status": "error",
                "error_type": "tool_exception",
                "message": str(e)
            }
            
        duration = int((time.time() - start_time) * 1000)
        
        # Ensure result has standard structure
        if "metadata" not in result:
            result["metadata"] = {}
        result["metadata"]["duration_ms"] = duration
        if "tool" not in result:
            result["tool"] = tool_name
            
        return result

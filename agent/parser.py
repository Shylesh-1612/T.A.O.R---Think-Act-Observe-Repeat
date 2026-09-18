import json
from typing import Dict, Any, Tuple

class AgentParser:
    @staticmethod
    def parse(llm_output: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Parses the LLM output and validates basic schema.
        Returns (is_valid, parsed_dict, error_message)
        """
        try:
            # Sometimes LLMs wrap json in markdown blocks
            clean_output = llm_output.strip()
            if clean_output.startswith("```json"):
                clean_output = clean_output[7:-3].strip()
            elif clean_output.startswith("```"):
                clean_output = clean_output[3:-3].strip()
                
            data = json.loads(clean_output)
        except json.JSONDecodeError as e:
            return False, {}, f"Invalid JSON format. Error: {str(e)}. Please respond with valid JSON only."

        action_type = data.get("type")
        if action_type not in ["tool_call", "final"]:
            return False, {}, "Missing or invalid 'type'. Must be 'tool_call' or 'final'."

        if action_type == "tool_call":
            if "tool" not in data or "input" not in data:
                return False, {}, "A 'tool_call' must include 'tool' and 'input' fields."
            
        if action_type == "final":
            if "answer" not in data:
                return False, {}, "A 'final' action must include an 'answer' field."

        return True, data, ""

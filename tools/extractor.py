from typing import Dict, Any
from .base import Tool
import re

class Extractor(Tool):
    name = "extractor"
    description = "Extracts structured data fields from raw text. Returns null for fields not found."
    input_schema = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "fields": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["text", "fields"]
    }

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("text", "")
        fields = input_data.get("fields", [])
        
        if not text:
            return {"status": "error", "tool": self.name, "error_type": "invalid_input", "message": "Missing text"}
            
        extracted = {}
        # In a genuine production setup without a framework, we might ping a lightweight LLM explicitly here.
        # For this hackathon, we simulate it via basic matching to avoid hidden recursive LLM calls.
        for field in fields:
            # Look for basic proximity of the field name to values (dates, money, or capitalized words)
            field_pattern = re.compile(rf"{re.escape(field)}.*?(\$?\d+[\d,.]*\b|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", re.IGNORECASE)
            match = field_pattern.search(text)
            
            if match:
                extracted[field] = match.group(1)
            else:
                extracted[field] = None
                
        return {"status": "success", "tool": self.name, "data": {"items": extracted}}

import json
from typing import List, Dict, Any, Optional
from .base import LLMBase

class MockLLM(LLMBase):
    def __init__(self, responses: List[str]):
        self.responses = responses
        self.call_count = 0

    def generate(self, messages: List[Dict[str, str]], response_schema: Optional[Any] = None) -> str:
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return json.dumps({"type": "final", "answer": "Mock LLM ran out of responses", "sources": []})

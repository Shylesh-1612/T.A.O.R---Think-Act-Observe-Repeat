from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMBase(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], response_schema: Optional[Any] = None) -> str:
        """Generate response given a list of messages. Optionally validate against a schema (if supported natively)."""
        pass

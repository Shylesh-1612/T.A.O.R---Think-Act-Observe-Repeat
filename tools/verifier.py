from typing import Dict, Any
from .base import Tool

class Verifier(Tool):
    name = "verifier"
    description = "Verifies a specific claim against a provided source text. Returns verified, unverified, or uncertain."
    input_schema = {
        "type": "object",
        "properties": {
            "claim": {"type": "string"},
            "source_text": {"type": "string"}
        },
        "required": ["claim", "source_text"]
    }

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        claim = input_data.get("claim", "")
        source_text = input_data.get("source_text", "")
        
        if not claim or not source_text:
            return {"status": "error", "tool": self.name, "error_type": "invalid_input", "message": "Missing claim or source_text"}

        # Simulate strict evidence-based verification
        claim_words = set(claim.lower().split())
        source_words = set(source_text.lower().split())
        
        # Simple overlap check for demonstration
        overlap = len(claim_words.intersection(source_words))
        
        if overlap > len(claim_words) * 0.6:
            verified = True
            confidence = "high"
            evidence = "Source text contains significant matching assertions."
        elif overlap > len(claim_words) * 0.3:
            verified = False
            confidence = "low"
            evidence = "Source text only partially matches the claim. Uncertain."
        else:
            verified = False
            confidence = "high"
            evidence = "Source text does not support the claim."

        return {
            "status": "success",
            "tool": self.name,
            "data": {
                "verified": verified,
                "confidence": confidence,
                "evidence": evidence,
                "source": "Provided source_text"
            }
        }

from typing import List, Dict, Any

class AgentState:
    def __init__(self, objective: str):
        self.objective = objective
        self.step_number = 0
        self.history: List[Dict[str, Any]] = []
        
    def add_event(self, event_type: str, data: Any):
        self.history.append({
            "step": self.step_number,
            "type": event_type,
            "data": data
        })

    def increment_step(self):
        self.step_number += 1
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "step_number": self.step_number,
            "history": self.history
        }

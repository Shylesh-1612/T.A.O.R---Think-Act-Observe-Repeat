import json
import logging
from typing import Dict, Any, Optional

from llm.base import LLMBase
from tools.registry import ToolRegistry
from agent.state import AgentState
from agent.parser import AgentParser
from agent.dispatcher import ToolDispatcher
from agent.prompts import build_messages

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NEXUS_AGENT")

class NexusAgent:
    def __init__(self, llm: LLMBase, registry: ToolRegistry, max_steps: int = 10):
        self.llm = llm
        self.registry = registry
        self.dispatcher = ToolDispatcher(registry)
        self.max_steps = max_steps

    def run(self, objective: str) -> Dict[str, Any]:
        logger.info(f"Starting NEXUS Agent. Objective: {objective}")
        state = AgentState(objective)
        
        # Loop detection tracker
        recent_actions = []

        for step in range(1, self.max_steps + 1):
            state.step_number = step
            logger.info(f"--- STEP {step} ---")
            
            # 1. PLAN / THINK (Build Context)
            messages = build_messages(state.objective, state.history, self.registry.get_descriptions())
            
            # 2. ACT (Ask LLM)
            try:
                llm_response = self.llm.generate(messages)
            except Exception as e:
                logger.error(f"LLM Generation failed: {e}")
                return {"status": "error", "message": f"LLM failure: {str(e)}", "state": state.to_dict()}
                
            # Parse Response
            is_valid, parsed_action, error_msg = AgentParser.parse(llm_response)
            
            if not is_valid:
                logger.warning(f"Malformed LLM output: {error_msg}")
                obs = {
                    "status": "error",
                    "error_type": "malformed_llm_output",
                    "message": error_msg,
                    "raw_output": llm_response
                }
                state.add_event("action", {"raw": llm_response})
                state.add_event("observation", obs)
                continue

            state.add_event("action", parsed_action)
            action_type = parsed_action.get("type")
            
            # Check for final answer
            if action_type == "final":
                logger.info("Agent decided to finish.")
                return {
                    "status": "success",
                    "final_answer": parsed_action,
                    "state": state.to_dict()
                }
                
            # Check for repeated actions (Loop Detection)
            action_str = json.dumps(parsed_action, sort_keys=True)
            if action_str in recent_actions[-2:]:
                logger.warning("Detected repeated action without useful progress.")
                obs = {
                    "status": "warning",
                    "error_type": "repeated_action",
                    "message": "The same action has been repeated without useful progress. Change strategy or finish."
                }
                state.add_event("observation", obs)
                recent_actions.append(action_str)
                continue
                
            recent_actions.append(action_str)
            if len(recent_actions) > 5:
                recent_actions.pop(0)
                
            # Execute Tool
            tool_name = parsed_action.get("tool")
            tool_input = parsed_action.get("input", {})
            reason = parsed_action.get("reason", "No reason provided")
            
            logger.info(f"PLAN/THINK: {reason}")
            logger.info(f"ACT: Tool: {tool_name} | Input: {tool_input}")
            
            observation = self.dispatcher.dispatch(tool_name, tool_input)
            
            # 3. OBSERVE
            logger.info(f"OBSERVE: {observation['status']} | {observation.get('error_type', '')}")
            state.add_event("observation", observation)

        # 4. End of max steps
        logger.warning("Maximum steps reached without finding a final answer.")
        return {
            "status": "error",
            "message": "Maximum steps reached.",
            "state": state.to_dict()
        }

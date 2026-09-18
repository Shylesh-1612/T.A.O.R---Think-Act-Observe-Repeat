import pytest
from unittest.mock import patch
from tools.registry import ToolRegistry
from tools.calculator import Calculator
from agent.core import NexusAgent
from llm.mock import MockLLM
from llm.provider import OpenAIProvider
import openai
import json
import os

def test_agent_success():
    registry = ToolRegistry()
    registry.register(Calculator())
    
    mock_responses = [
        json.dumps({
            "type": "tool_call",
            "tool": "calculator",
            "input": {"expression": "10 * 10"},
            "reason": "Need to calculate."
        }),
        json.dumps({
            "type": "final",
            "answer": "The answer is 100.",
            "sources": []
        })
    ]
    llm = MockLLM(mock_responses)
    
    agent = NexusAgent(llm, registry)
    result = agent.run("What is 10 * 10?")
    
    assert result["status"] == "success"
    assert result["final_answer"]["answer"] == "The answer is 100."
    assert result["state"]["step_number"] == 2

def test_agent_unknown_tool():
    registry = ToolRegistry()
    
    mock_responses = [
        json.dumps({
            "type": "tool_call",
            "tool": "fake_tool",
            "input": {},
            "reason": "Test"
        }),
        json.dumps({
            "type": "final",
            "answer": "Done.",
            "sources": []
        })
    ]
    llm = MockLLM(mock_responses)
    
    agent = NexusAgent(llm, registry)
    result = agent.run("Do something.")
    
    assert result["status"] == "success"
    history = result["state"]["history"]
    obs = [item for item in history if item["type"] == "observation"][0]
    assert obs["data"]["status"] == "error"
    assert obs["data"]["error_type"] == "unknown_tool"

def test_agent_malformed_output():
    registry = ToolRegistry()
    
    mock_responses = [
        "This is not JSON",
        json.dumps({
            "type": "final",
            "answer": "Fixed it.",
            "sources": []
        })
    ]
    llm = MockLLM(mock_responses)
    
    agent = NexusAgent(llm, registry)
    result = agent.run("Do something.")
    
    assert result["status"] == "success"
    history = result["state"]["history"]
    obs = [item for item in history if item["type"] == "observation"][0]
    assert obs["data"]["status"] == "error"
    assert obs["data"]["error_type"] == "malformed_llm_output"

def test_agent_max_steps():
    registry = ToolRegistry()
    mock_responses = [
        json.dumps({
            "type": "tool_call",
            "tool": "fake_tool",
            "input": {},
            "reason": "Test"
        })
    ] * 20
    llm = MockLLM(mock_responses)
    
    agent = NexusAgent(llm, registry, max_steps=3)
    result = agent.run("Loop forever.")
    
    assert result["status"] == "error"
    assert result["message"] == "Maximum steps reached."

def test_openai_provider_missing_key():
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    with pytest.raises(ValueError):
        OpenAIProvider()

@patch('llm.provider.openai.OpenAI')
def test_openai_provider_auth_error(mock_openai):
    os.environ["OPENAI_API_KEY"] = "fake"
    provider = OpenAIProvider()
    from unittest.mock import MagicMock
    mock_response = MagicMock()
    mock_response.request = MagicMock()
    provider.client.chat.completions.create.side_effect = openai.AuthenticationError("Auth failed", response=mock_response, body=None)
    with pytest.raises(RuntimeError) as exc:
        provider.generate([])
    assert "Authentication failed" in str(exc.value)

@patch('llm.provider.openai.OpenAI')
def test_openai_provider_rate_limit(mock_openai):
    os.environ["OPENAI_API_KEY"] = "fake"
    provider = OpenAIProvider()
    from unittest.mock import MagicMock
    mock_response = MagicMock()
    mock_response.request = MagicMock()
    provider.client.chat.completions.create.side_effect = openai.RateLimitError("Rate limited", response=mock_response, body=None)
    with pytest.raises(RuntimeError) as exc:
        provider.generate([])
    assert "Rate limit exceeded" in str(exc.value)

def test_agent_repeated_action():
    registry = ToolRegistry()
    registry.register(Calculator())
    
    # Send the identical action multiple times
    action_json = json.dumps({
        "type": "tool_call",
        "tool": "calculator",
        "input": {"expression": "2+2"},
        "reason": "Calculate"
    })
    
    mock_responses = [
        action_json,
        action_json,
        action_json,
        json.dumps({
            "type": "final",
            "answer": "Done.",
            "sources": []
        })
    ]
    llm = MockLLM(mock_responses)
    agent = NexusAgent(llm, registry, max_steps=5)
    result = agent.run("Test loop detection")
    
    history = result["state"]["history"]
    warnings = [item for item in history if item.get("type") == "observation" and item["data"].get("status") == "warning"]
    assert len(warnings) > 0
    assert warnings[0]["data"]["error_type"] == "repeated_action"


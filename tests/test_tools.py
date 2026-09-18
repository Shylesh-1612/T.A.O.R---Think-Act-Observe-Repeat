import pytest
from tools.calculator import Calculator
from tools.web_search import WebSearch
from tools.extractor import Extractor
from tools.verifier import Verifier
from tools.unreliable_demo_tool import UnreliableDemoTool
import os

def test_calculator_success():
    calc = Calculator()
    res = calc.run({"expression": "2 + 2 * 3"})
    assert res["status"] == "success"
    assert res["data"]["result"] == 8

def test_calculator_zero_div():
    calc = Calculator()
    res = calc.run({"expression": "10 / 0"})
    assert res["status"] == "error"
    assert res["error_type"] == "division_by_zero"

def test_calculator_invalid():
    calc = Calculator()
    res = calc.run({"expression": "10 + foo"})
    assert res["status"] == "error"
    assert res["error_type"] == "malformed_input"

def test_web_search_success():
    search = WebSearch()
    # It hits actual Wikipedia API but should be fast
    res = search.run({"query": "Python (programming language)"})
    assert res["status"] == "success"
    assert "results" in res["data"]
    
def test_extractor():
    ext = Extractor()
    res = ext.run({"text": "The event costs $100.", "fields": ["cost"]})
    assert res["status"] == "success"
    assert "cost" in res["data"]["items"]

def test_verifier():
    ver = Verifier()
    res = ver.run({"claim": "This is a real claim", "source_text": "Wikipedia This is a real claim"})
    assert res["status"] == "success"
    assert res["data"]["verified"] is True
    
def test_unreliable_tool_demo_mode_off():
    os.environ["DEMO_FAILURE_MODE"] = "false"
    tool = UnreliableDemoTool()
    res = tool.run({"query": "test"})
    assert res["status"] == "success"

def test_unreliable_tool_demo_mode_on():
    os.environ["DEMO_FAILURE_MODE"] = "true"
    tool = UnreliableDemoTool()
    res1 = tool.run({"query": "test"})
    assert res1["status"] == "error"
    assert res1["error_type"] == "network_failure"
    
    res2 = tool.run({"query": "test"})
    assert res2["status"] == "error"
    assert res2["error_type"] == "malformed_result"
    
    res3 = tool.run({"query": "test"})
    assert res3["status"] == "success"

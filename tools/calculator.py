import ast
import operator
from typing import Dict, Any
from .base import Tool

class Calculator(Tool):
    name = "calculator"
    description = "Evaluates basic mathematical expressions. Input must be a valid simple expression string."
    input_schema = {
        "type": "object",
        "properties": {
            "expression": {"type": "string"}
        },
        "required": ["expression"]
    }

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        expr = input_data.get("expression", "")
        if not expr:
            return {"status": "error", "error_type": "invalid_input", "message": "Missing expression"}

        allowed_operators = {
            ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
            ast.BitXor: operator.xor
        }

        def _eval(node):
            if hasattr(ast, "Num") and isinstance(node, getattr(ast, "Num")): # for python < 3.8
                return node.n
            elif hasattr(ast, "Constant") and isinstance(node, getattr(ast, "Constant")): # python >= 3.8
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Unsupported constant")
            elif isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                op = allowed_operators[type(node.op)]
                return op(left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                op = allowed_operators[type(node.op)]
                return op(operand)
            else:
                raise TypeError(f"Unsupported ast node {node}")

        try:
            node = ast.parse(expr, mode='eval').body
            result = _eval(node)
            return {"status": "success", "tool": self.name, "data": {"result": result}}
        except ZeroDivisionError:
            return {"status": "error", "tool": self.name, "error_type": "division_by_zero", "message": "Division by zero"}
        except Exception as e:
            return {"status": "error", "tool": self.name, "error_type": "malformed_input", "message": str(e)}

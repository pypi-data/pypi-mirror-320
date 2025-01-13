from .base_tool import BaseTool
from typing import Dict, Any

class CalculatorTool(BaseTool):
    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a calculation.

        Args:
            input (Dict[str, Any]): Input data containing the expression.

        Returns:
            Dict[str, Any]: Output data containing the result.
        """
        expression = input.get("expression", "")
        try:
            result = eval(expression)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
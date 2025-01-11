from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """
    Base class for all tools. Subclasses must implement the `run` method.
    """

    @abstractmethod
    def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the tool with the given input.

        Args:
            input (Dict[str, Any]): Input data for the tool.

        Returns:
            Dict[str, Any]: Output data from the tool.
        """
        pass
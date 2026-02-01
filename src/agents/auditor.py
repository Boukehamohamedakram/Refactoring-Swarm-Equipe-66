"""Auditor agent for code analysis."""

from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent
from src.utils.logger import ActionType


class Auditor(BaseAgent):
    """Agent responsible for analyzing code and identifying issues."""

    def __init__(self, model: str = "mistral-large-latest"):
        """Initialize the auditor agent.
        
        Args:
            model: Gemini model to use
        """
        super().__init__(
            agent_name="Auditor",
            prompt_file="src/prompts/auditor_prompt.txt",
            model=model
        )

    def analyze(self, file_path: str, code: str) -> Dict[str, Any]:
        """Analyze code for issues.
        
        Args:
            file_path: Path to the file being analyzed
            code: Source code to analyze
            
        Returns:
            Dictionary with analysis results and list of issues
        """
        user_message = f"""
Please analyze the following Python file: {file_path}

Code:
```python
{code}
```

Provide a comprehensive analysis of issues, their severity, and recommendations.
"""
        
        try:
            response = self.call_mistral_api(user_message)
            result = self._parse_json_response(response)
            
            # Log the interaction
            self.log_interaction(
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": user_message,
                    "output_response": response,
                    "file": file_path
                },
                status="SUCCESS"
            )
            
            return result
            
        except Exception as e:
            error_response = {"file": file_path, "error": str(e), "issues": []}
            self.log_interaction(
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": user_message,
                    "output_response": str(e),
                    "file": file_path
                },
                status="FAILURE"
            )
            return error_response

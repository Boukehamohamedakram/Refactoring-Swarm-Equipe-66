"""Fixer agent for code refactoring."""

from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent
from src.utils.logger import ActionType


class Fixer(BaseAgent):
    """Agent responsible for fixing code issues."""

    def __init__(self, model: str = "gemma-3-4b-it"):
        """Initialize the fixer agent.
        
        Args:
            model: Gemini model to use
        """
        super().__init__(
            agent_name="Fixer",
            prompt_file="src/prompts/fixer_prompt.txt",
            model=model
        )

    def analyze(self, **kwargs) -> Dict[str, Any]:
        """Not used for Fixer - use fix() instead."""
        raise NotImplementedError("Use fix() method instead")

    def fix(self, file_path: str, code: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fix identified issues in code.
        
        Args:
            file_path: Path to the file being fixed
            code: Original source code
            issues: List of issues from auditor
            
        Returns:
            Dictionary with fixed code and changes made
        """
        issues_str = "\n".join([
            f"- [{issue.get('severity', 'UNKNOWN')}] {issue.get('type', 'Unknown')}: {issue.get('description', '')}"
            for issue in issues
        ])
        
        user_message = f"""
Please fix the following issues in: {file_path}

Issues to fix:
{issues_str}

Original code:
```python
{code}
```

Apply targeted fixes for each issue while maintaining functionality.
Return the complete refactored code and explain each change made.
"""
        
        try:
            response = self.call_mistral_api(user_message)
            result = self._parse_json_response(response)
            
            # Log the interaction
            self.log_interaction(
                action=ActionType.FIX,
                details={
                    "input_prompt": user_message,
                    "output_response": response,
                    "file": file_path,
                    "issues_count": len(issues)
                },
                status="SUCCESS"
            )
            
            return result
            
        except Exception as e:
            error_response = {"file": file_path, "error": str(e), "refactored_code": code}
            self.log_interaction(
                action=ActionType.FIX,
                details={
                    "input_prompt": user_message,
                    "output_response": str(e),
                    "file": file_path
                },
                status="FAILURE"
            )
            return error_response

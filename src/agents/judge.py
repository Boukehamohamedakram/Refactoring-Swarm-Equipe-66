"""Judge agent for validating refactored code."""

from typing import Any, Dict

from src.agents.base_agent import BaseAgent
from src.utils.logger import ActionType


class Judge(BaseAgent):
    """Agent responsible for validating refactored code quality."""

    def __init__(self, model: str = "gemma-3-4b-it"):
        """Initialize the judge agent.
        
        Args:
            model: Gemini model to use
        """
        super().__init__(
            agent_name="Judge",
            prompt_file="src/prompts/judge_prompt.txt",
            model=model
        )

    def analyze(self, **kwargs) -> Dict[str, Any]:
        """Not used for Judge - use validate() instead."""
        raise NotImplementedError("Use validate() method instead")

    def validate(
        self,
        file_path: str,
        original_code: str,
        refactored_code: str,
        changes_summary: str
    ) -> Dict[str, Any]:
        """Validate the quality of refactored code.
        
        Args:
            file_path: Path to the file
            original_code: Original source code
            refactored_code: Refactored source code
            changes_summary: Summary of changes made
            
        Returns:
            Dictionary with validation verdict and feedback
        """
        user_message = f"""
Please validate the refactored code for quality and correctness.

File: {file_path}

Original Code:
```python
{original_code}
```

Refactored Code:
```python
{refactored_code}
```

Changes Made:
{changes_summary}

Evaluate if the refactoring is an improvement and if any additional changes are needed.
Return a verdict: APPROVED, NEEDS_REVISION, or REJECTED, along with detailed feedback.
"""
        
        try:
            response = self.call_gemini_api(user_message)
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
            error_response = {
                "file": file_path,
                "error": str(e),
                "verdict": "REJECTED"
            }
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

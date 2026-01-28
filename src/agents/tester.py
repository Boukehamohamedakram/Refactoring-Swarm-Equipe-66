"""Tester agent for generating and validating unit tests."""

from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent
from src.utils.logger import ActionType


class Tester(BaseAgent):
    """Agent responsible for generating unit tests to verify refactored code."""

    def __init__(self, model: str = "mistral-large-latest"):
        """Initialize the tester agent.
        
        Args:
            model: Mistral model to use
        """
        super().__init__(
            agent_name="Tester",
            prompt_file="src/prompts/tester_prompt.txt",
            model=model
        )

    def analyze(self, **kwargs) -> Dict[str, Any]:
        """Placeholder analyze method (Tester uses generate_tests instead).
        
        Returns:
            Empty analysis result
        """
        return {"issues": []}

    def generate_tests(self, file_path: str, code: str, original_code: str = None) -> Dict[str, Any]:
        """Generate unit tests for the refactored code.
        
        Args:
            file_path: Path to the file being tested
            code: Refactored source code
            original_code: Original code (optional, for comparison)
            
        Returns:
            Dictionary with generated test code and metadata
        """
        comparison_note = ""
        if original_code:
            comparison_note = "\n\nOriginal code (for reference):\n```python\n" + original_code + "\n```"
        
        user_message = f"""
Generate comprehensive unit tests for the following Python file: {file_path}

Refactored code:
```python
{code}
```
{comparison_note}

Requirements:
1. Create tests that verify the main functionality of the code
2. Include edge case tests
3. Ensure tests are independent and can run with pytest
4. Return valid, executable Python code
5. Use clear test names that describe what is being tested

Format your response as JSON with the following structure:
{{
    "test_code": "the complete test file content as a string",
    "test_count": number of test functions,
    "coverage_areas": ["area1", "area2", ...],
    "notes": "any notes about the tests"
}}
"""
        
        try:
            response = self.call_mistral_api(user_message)
            result = self._parse_json_response(response)
            
            # Log the interaction
            self.log_interaction(
                action=ActionType.GENERATION,
                prompt=user_message,
                response=response,
                status="SUCCESS" if result else "FAILURE"
            )
            
            return result
        except Exception as e:
            error_msg = str(e)
            self.log_interaction(
                action=ActionType.DEBUG,
                prompt=user_message,
                response=error_msg,
                status="FAILURE"
            )
            return {
                "error": error_msg,
                "test_code": "",
                "test_count": 0,
                "coverage_areas": []
            }

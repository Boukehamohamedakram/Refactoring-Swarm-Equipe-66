"""Utility tools for the refactoring swarm system."""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any


def discover_python_files(target_dir: str) -> List[str]:
    """Discover all Python files in a directory.
    
    Args:
        target_dir: Directory to search
        
    Returns:
        List of absolute paths to Python files
    """
    python_files = []
    for root, dirs, files in os.walk(target_dir):
        # Skip common non-essential directories
        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git', 'venv', '.venv', 'node_modules'}]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def read_file(file_path: str) -> str:
    """Read file content.
    
    Args:
        file_path: Path to file
        
    Returns:
        File content as string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write content to file.
    
    Args:
        file_path: Path to file
        content: Content to write
    """
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def validate_syntax(code: str, file_path: str = None) -> Dict[str, Any]:
    """Validate Python syntax.
    
    Args:
        code: Python code to validate
        file_path: Optional file path for error messages
        
    Returns:
        Dictionary with validation result
    """
    try:
        compile(code, file_path or '<string>', 'exec')
        return {"valid": True, "errors": []}
    except SyntaxError as e:
        return {
            "valid": False,
            "errors": [{
                "line": e.lineno,
                "offset": e.offset,
                "text": e.text,
                "msg": e.msg
            }]
        }


def run_tests(test_dir: str = "tests") -> Dict[str, Any]:
    """Run pytest on a directory.
    
    Args:
        test_dir: Directory containing tests
        
    Returns:
        Dictionary with test results
    """
    try:
        result = subprocess.run(
            ["pytest", test_dir, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "error": "Tests timed out after 30 seconds",
            "stdout": "",
            "stderr": ""
        }
    except Exception as e:
        return {
            "passed": False,
            "error": str(e),
            "stdout": "",
            "stderr": ""
        }

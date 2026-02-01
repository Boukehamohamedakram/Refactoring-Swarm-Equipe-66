"""Utility tools for the refactoring swarm system."""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
import re

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

def run_pylint_test(file_path:str) -> Dict[str,Any]:
    """
    Runs pylint on a file

    Args:
        file_path: path of the file
        
    Returns:
        Dictionary with score,issues,exit code, stderr
    """

    file_path = str(Path(file_path).resolve())

    command = [
        "pylint",
        file_path,
        "--output-format=json",
        "--score=y",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    try:
        issues = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        issues = []

    score = get_pylint_score(file_path)

    return {
        "score": score,
        "issues": issues,
        "exit_code": result.returncode,
        "stderr": result.stderr,
    }

def get_pylint_score(file_path: str) -> float | None:
    """
    Runs pylint on a single file and returns the numeric score (0-10),
    or None if pylint fails to compute a score (e.g., syntax error).
    and beacuase the first one doesnt give the score directly 

    Args:
        file_path: path of the file
        
    Returns:
        score or None
    """
    command = [
        "pylint",
        file_path,
        "--score=y",
        "--reports=n"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    match = re.search(r"rated at ([0-9.]+)/10", result.stdout)
    if match:
        return float(match.group(1))

    return None

def change_file_path(file_path: str,target_dir: str="sandbox") -> str:
    
    """
   change the file path so it will be in the target_dir
    """
    sandbox_dir = Path.cwd() / target_dir
    
    # check if the sandbox is a directory
    sandbox_dir.mkdir(parents=True,exist_ok=True)
    
    file_path = sandbox_dir / Path(file_path).name
    
    return file_path

def check_file_in_sandbox(file_path: str) -> bool:
    """check if a file is directly inside the sandbox folder"""
    
    sandbox_dir = Path("./sandbox").resolve()
    path = Path(file_path).resolve()

    if path.parent == sandbox_dir:
        return True
    return False
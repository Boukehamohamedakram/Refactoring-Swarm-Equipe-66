"""Shared utility functions for the refactoring swarm system."""

from pathlib import Path
from typing import List


def discover_python_files(target_dir: str) -> List[Path]:
    """Discover all Python files in target directory.
    
    Args:
        target_dir: Root directory to scan
        
    Returns:
        List of Path objects for Python files
    """
    target = Path(target_dir).resolve()
    return list(target.rglob("*.py"))


def get_directory_stats(target_dir: str) -> dict:
    """Get basic statistics about target directory.
    
    Args:
        target_dir: Root directory to analyze
        
    Returns:
        Dictionary with stats (file count, subdirs, etc.)
    """
    target = Path(target_dir).resolve()
    py_files = discover_python_files(target_dir)
    
    stats = {
        "root": str(target),
        "exists": target.exists(),
        "is_directory": target.is_dir(),
        "python_files": len(py_files),
        "subdirectories": len(list(target.iterdir()) if target.is_dir() else []),
    }
    return stats

"""Orchestrator for coordinating the refactoring swarm agents."""

import os
from typing import Dict, List, Any
from pathlib import Path

from src.agents.auditor import Auditor
from src.agents.fixer import Fixer
from src.agents.judge import Judge
from src.tools import (
    discover_python_files,
    read_file,
    write_file,
    validate_syntax,
    run_tests
)


class Orchestrator:
    """Orchestrates the refactoring workflow across multiple agents."""

    def __init__(self, max_iterations: int = 10):
        """Initialize the orchestrator.
        
        Args:
            max_iterations: Maximum number of refactoring iterations per file
        """
        self.max_iterations = max_iterations
        self.auditor = Auditor()
        self.fixer = Fixer()
        self.judge = Judge()
        self.results = {}

    def refactor_directory(self, target_dir: str) -> Dict[str, Any]:
        """Refactor all Python files in a directory.
        
        Args:
            target_dir: Directory containing files to refactor
            
        Returns:
            Results dictionary with refactoring status
        """
        # Discover Python files
        python_files = discover_python_files(target_dir)
        print(f"\n[INFO] Discovered {len(python_files)} Python files")
        
        # Process each file
        for file_path in python_files:
            print(f"\n[File] Refactoring: {file_path}")
            self.refactor_file(file_path)
        
        return {
            "status": "completed",
            "files_processed": len(python_files),
            "results": self.results
        }

    def refactor_file(self, file_path: str) -> Dict[str, Any]:
        """Refactor a single Python file through the agent workflow.
        
        Args:
            file_path: Path to file to refactor
            
        Returns:
            Refactoring results for this file
        """
        # Read original code
        try:
            original_code = read_file(file_path)
        except Exception as e:
            print(f"[ERROR] Failed to read {file_path}: {e}")
            return {"status": "error", "error": str(e)}
        
        current_code = original_code
        iteration = 0
        file_improved = False
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n============================================================")
            print(f"[Iteration {iteration}/{self.max_iterations}]")
            print(f"============================================================")
            
            # Step 1: Auditor analyzes code
            print(f"\n[Auditor] Analyzing {Path(file_path).name}...")
            analysis = self.auditor.analyze(file_path, current_code)
            
            issues = analysis.get("issues", [])
            if not issues:
                print(f"[SUCCESS] No issues found. Refactoring complete!")
                file_improved = True
                break
            
            issue_count = len(issues)
            print(f"[WARN] Found {issue_count} issues")
            
            # Step 2: Fixer applies fixes
            print(f"\n[Fixer] Applying fixes...")
            fix_result = self.fixer.fix(file_path, current_code, issues)
            
            # Check if fixes were actually applied
            if "error" in fix_result:
                print(f"[ERROR] Fixer failed: {fix_result.get('error', 'Unknown error')}")
                print(f"[INFO] No fixes applied")
                break
            
            refactored_code = fix_result.get("refactored_code", current_code)
            changes = fix_result.get("changes", [])
            changes_count = len(changes)
            print(f"[FIX] Applied {changes_count} fixes")
            
            # Validate syntax
            validation = validate_syntax(refactored_code, file_path)
            if not validation["valid"]:
                print(f"[ERROR] Refactored code has syntax errors")
                break
            
            # Step 3: Judge validates quality
            print(f"\n[Judge] Validating refactored code...")
            changes_summary = "\n".join([
                f"- {c.get('change_description', '')}"
                for c in changes
            ])
            
            judgment = self.judge.validate(
                file_path,
                current_code,
                refactored_code,
                changes_summary or "Code refactored"
            )
            
            verdict = judgment.get("verdict", "REJECTED")
            print(f"[VERDICT] Judge: {verdict}")
            
            if verdict == "APPROVED":
                # Write the refactored code
                write_file(file_path, refactored_code)
                current_code = refactored_code
                file_improved = True
                
                # Run tests
                print(f"\n[Testing] Running pytest...")
                test_result = run_tests("tests" if os.path.exists("tests") else "sandbox/test")
                if test_result.get("passed"):
                    print(f"Tests: PASSED")
                    print(f"[SUCCESS] Refactoring completed successfully!")
                    break
                else:
                    print(f"Tests: FAILED")
                    # Continue iterating if tests fail
                    
            elif verdict == "NEEDS_REVISION":
                feedback = judgment.get("feedback", "No feedback")
                print(f"[ERROR] Refactoring rejected: {feedback}")
                break
                
            elif verdict == "REJECTED":
                feedback = judgment.get("feedback", "No feedback")
                print(f"[ERROR] Refactoring rejected: {feedback}")
                break
        
        if iteration >= self.max_iterations:
            print(f"\n[WARNING] Reached maximum iterations ({self.max_iterations})")
        
        self.results[file_path] = {
            "iterations": iteration,
            "improved": file_improved,
            "original_size": len(original_code),
            "final_size": len(current_code)
        }
        
        return self.results[file_path]

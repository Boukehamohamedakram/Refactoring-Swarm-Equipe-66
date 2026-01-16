"""Orchestrator for coordinating the refactoring swarm agents."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add the parent directory (project root) to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

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

    def _analyze_code(self, file_path: str, code: str) -> List[Dict[str, Any]]:
        """Analyze code for issues using the auditor.
        
        Args:
            file_path: Path to the file
            code: Code content
            
        Returns:
            List of issues found
        """
        analysis = self.auditor.analyze(file_path, code)
        return analysis.get("issues", [])

    def _apply_fixes(self, file_path: str, code: str, issues: List[Dict[str, Any]]) -> tuple[str | None, List[Dict[str, Any]]]:
        """Apply fixes to the code using the fixer.
        
        Args:
            file_path: Path to the file
            code: Current code content
            issues: List of issues to fix
            
        Returns:
            Tuple of (refactored_code, changes) or (None, []) if error
        """
        fix_result = self.fixer.fix(file_path, code, issues)
        if "error" in fix_result:
            return None, []
        refactored_code = fix_result.get("refactored_code", code)
        changes = fix_result.get("changes", [])
        return refactored_code, changes

    def _validate_refactored_code(self, code: str, file_path: str) -> bool:
        """Validate the syntax of refactored code.
        
        Args:
            code: Refactored code
            file_path: Path to the file
            
        Returns:
            True if valid, False otherwise
        """
        validation = validate_syntax(code, file_path)
        return validation.get("valid", False)

    def _judge_changes(self, file_path: str, original_code: str, refactored_code: str, changes_summary: str) -> Dict[str, Any]:
        """Judge the quality of changes using the judge.
        
        Args:
            file_path: Path to the file
            original_code: Original code
            refactored_code: Refactored code
            changes_summary: Summary of changes
            
        Returns:
            Judgment dictionary from the judge
        """
        judgment = self.judge.validate(
            file_path,
            original_code,
            refactored_code,
            changes_summary or "Code refactored"
        )
        return judgment

    def _run_and_check_tests(self) -> bool:
        """Run tests and check if they pass.
        
        Returns:
            True if tests pass, False otherwise
        """
        test_result = run_tests("tests" if os.path.exists("tests") else "sandbox/test")
        return test_result.get("passed", False)

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
            
            # Step 1: Analyze code
            print(f"\n[Auditor] Analyzing {Path(file_path).name}...")
            issues = self._analyze_code(file_path, current_code)
            if not issues:
                print(f"[SUCCESS] No issues found. Refactoring complete!")
                file_improved = True
                break
            
            issue_count = len(issues)
            print(f"[WARN] Found {issue_count} issues")
            
            # Step 2: Apply fixes
            print(f"\n[Fixer] Applying fixes...")
            refactored_code, changes = self._apply_fixes(file_path, current_code, issues)
            if refactored_code is None:
                print(f"[ERROR] Fixer failed")
                print(f"[INFO] No fixes applied")
                break
            
            changes_count = len(changes)
            print(f"[FIX] Applied {changes_count} fixes")
            
            # Validate syntax
            if not self._validate_refactored_code(refactored_code, file_path):
                print(f"[ERROR] Refactored code has syntax errors")
                break
            
            # Step 3: Judge changes
            print(f"\n[Judge] Validating refactored code...")
            changes_summary = "\n".join([
                f"- {c.get('change_description', '')}"
                for c in changes
            ])
            
            judgment = self._judge_changes(
                file_path,
                current_code,
                refactored_code,
                changes_summary
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
                if self._run_and_check_tests():
                    print(f"Tests: PASSED")
                    print(f"[SUCCESS] Refactoring completed successfully!")
                    break
                else:
                    print(f"Tests: FAILED")
                    # Continue iterating if tests fail
                    
            elif verdict == "NEEDS_REVISION":
                feedback = judgment.get("feedback", "No feedback")
                print(f"[ERROR] Refactoring needs revision: {feedback}")
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

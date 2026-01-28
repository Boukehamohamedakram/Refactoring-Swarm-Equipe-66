"""Orchestrator for coordinating the refactoring swarm agents."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, TypedDict

# Add the parent directory (project root) to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.auditor import Auditor
from src.agents.fixer import Fixer
from src.agents.judge import Judge
from src.agents.tester import Tester
from src.tools import (
    discover_python_files,
    read_file,
    write_file,
    validate_syntax,
    run_tests
)
from src.utils.logger import log_experiment, ActionType


# Define the state structure for workflow orchestration
class RefactoringState(TypedDict, total=False):
    """State for the refactoring workflow."""
    file_path: str
    original_code: str
    current_code: str
    iteration: int
    issues: List[Dict[str, Any]]
    refactored_code: str
    changes: List[Dict[str, Any]]
    verdict: str
    feedback: str
    tests_passed: bool
    file_improved: bool
    error: str
    test_code: str
    test_error: str
    feedback_loop_count: int


class Orchestrator:
    """Orchestrates the refactoring workflow across multiple agents with state management."""

    def __init__(self, max_iterations: int = 10):
        """Initialize the orchestrator with state machine.
        
        Args:
            max_iterations: Maximum number of refactoring iterations per file
        """
        self.max_iterations = max_iterations
        self.auditor = Auditor()
        self.fixer = Fixer()
        self.judge = Judge()
        self.tester = Tester()
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

    # State machine node functions
    def _node_analyze(self, state: RefactoringState) -> RefactoringState:
        """State node: Analyze code for issues."""
        state["iteration"] += 1
        print(f"\n[Iteration {state['iteration']}/{self.max_iterations}] Analyzing...")
        
        issues = self._analyze_code(state["file_path"], state["current_code"])
        state["issues"] = issues
        
        log_experiment(
            agent_name="Auditor",
            model_used="mistral-large-latest",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Analyze {Path(state['file_path']).name}",
                "output_response": f"Found {len(issues)} issues",
                "issues_count": len(issues)
            },
            status="SUCCESS"
        )
        
        return state

    def _node_apply_fixes(self, state: RefactoringState) -> RefactoringState:
        """State node: Apply fixes to code."""
        print(f"[{state['iteration']}] Applying fixes...")
        
        refactored_code, changes = self._apply_fixes(
            state["file_path"],
            state["current_code"],
            state["issues"]
        )
        
        if refactored_code is None:
            state["error"] = "Fixer failed to generate refactored code"
            print(f"[ERROR] {state['error']}")
            return state
        
        state["refactored_code"] = refactored_code
        state["changes"] = changes
        
        log_experiment(
            agent_name="Fixer",
            model_used="mistral-large-latest",
            action=ActionType.GENERATION,
            details={
                "input_prompt": f"Fix issues in {Path(state['file_path']).name}",
                "output_response": f"Applied {len(changes)} fixes",
                "changes_count": len(changes)
            },
            status="SUCCESS"
        )
        
        return state

    def _node_validate(self, state: RefactoringState) -> RefactoringState:
        """State node: Validate refactored code syntax."""
        print(f"[{state['iteration']}] Validating syntax...")
        
        is_valid = self._validate_refactored_code(state["refactored_code"], state["file_path"])
        
        if not is_valid:
            state["error"] = "Refactored code has syntax errors"
            print(f"[ERROR] {state['error']}")
            return state
        
        log_experiment(
            agent_name="Orchestrator",
            model_used="SYSTEM",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Validate {Path(state['file_path']).name}",
                "output_response": "Syntax validation passed"
            },
            status="SUCCESS"
        )
        
        return state

    def _node_judge(self, state: RefactoringState) -> RefactoringState:
        """State node: Judge changes quality."""
        print(f"[{state['iteration']}] Judge validating...")
        
        changes_summary = "\n".join([
            f"- {c.get('change_description', '')}"
            for c in state["changes"]
        ])
        
        judgment = self._judge_changes(
            state["file_path"],
            state["current_code"],
            state["refactored_code"],
            changes_summary
        )
        
        state["verdict"] = judgment.get("verdict", "REJECTED")
        state["feedback"] = judgment.get("feedback", "")
        
        log_experiment(
            agent_name="Judge",
            model_used="mistral-large-latest",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Judge changes for {Path(state['file_path']).name}",
                "output_response": f"Verdict: {state['verdict']}",
                "verdict": state["verdict"],
                "feedback": state["feedback"]
            },
            status="SUCCESS"
        )
        
        return state

    def _node_write_changes(self, state: RefactoringState) -> RefactoringState:
        """State node: Write approved changes to file."""
        print(f"[{state['iteration']}] Writing changes...")
        
        try:
            write_file(state["file_path"], state["refactored_code"])
            state["current_code"] = state["refactored_code"]
            state["file_improved"] = True
            
            log_experiment(
                agent_name="Orchestrator",
                model_used="SYSTEM",
                action=ActionType.FIX,
                details={
                    "input_prompt": f"Write changes to {Path(state['file_path']).name}",
                    "output_response": "Changes written successfully",
                    "file": state["file_path"]
                },
                status="SUCCESS"
            )
        except Exception as e:
            state["error"] = f"Failed to write changes: {str(e)}"
            print(f"[ERROR] {state['error']}")
        
        return state

    def _node_run_tests(self, state: RefactoringState) -> RefactoringState:
        """State node: Run tests on refactored code."""
        print(f"[{state['iteration']}] Running tests...")
        
        tests_passed = self._run_and_check_tests()
        state["tests_passed"] = tests_passed
        
        log_experiment(
            agent_name="Orchestrator",
            model_used="SYSTEM",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Run tests for {Path(state['file_path']).name}",
                "output_response": f"Tests {'PASSED' if tests_passed else 'FAILED'}",
                "tests_passed": tests_passed
            },
            status="SUCCESS" if tests_passed else "FAILURE"
        )
        
        return state

    def _node_generate_tests(self, state: RefactoringState) -> RefactoringState:
        """State node: Generate unit tests for the refactored code."""
        print(f"[{state['iteration']}] Generating unit tests...")
        
        test_result = self.tester.generate_tests(
            state["file_path"],
            state["current_code"],
            state["original_code"]
        )
        
        if "error" in test_result:
            state["test_error"] = test_result.get("error", "Unknown error")
            print(f"[WARN] Test generation failed: {state['test_error']}")
            return state
        
        state["test_code"] = test_result.get("test_code", "")
        test_count = test_result.get("test_count", 0)
        
        log_experiment(
            agent_name="Tester",
            model_used="mistral-large-latest",
            action=ActionType.GENERATION,
            details={
                "input_prompt": f"Generate tests for {Path(state['file_path']).name}",
                "output_response": f"Generated {test_count} test functions",
                "test_count": test_count,
                "coverage_areas": test_result.get("coverage_areas", [])
            },
            status="SUCCESS"
        )
        
        return state

    def _node_feedback_loop(self, state: RefactoringState) -> RefactoringState:
        """State node: Implement feedback loop for test failures."""
        if state.get("tests_passed"):
            return state
        
        # Tests failed - initiate feedback loop
        state["feedback_loop_count"] = state.get("feedback_loop_count", 0) + 1
        
        if state["feedback_loop_count"] > 2:
            print(f"[INFO] Feedback loop limit reached ({state['feedback_loop_count']} attempts)")
            return state
        
        print(f"[FEEDBACK LOOP] Attempt {state['feedback_loop_count']}: Requesting Fixer to address test failures...")
        
        # Create feedback message with test failure details
        feedback_msg = f"""
Test execution failed. Please fix the code to make the tests pass.

Current issues:
- Tests are failing after refactoring
- The refactored code needs adjustments

Please analyze the refactored code and apply additional fixes.
Focus on functionality that would make the generated tests pass.
"""
        
        # Re-run fixer with feedback
        print(f"[{state['iteration']}] Applying fixes based on test feedback...")
        refactored_code, changes = self._apply_fixes(
            state["file_path"],
            state["current_code"],
            [{"issue": "Test failure", "description": feedback_msg}]
        )
        
        if refactored_code is None:
            state["error"] = "Fixer failed in feedback loop"
            print(f"[ERROR] {state['error']}")
            return state
        
        state["refactored_code"] = refactored_code
        state["changes"] = changes
        
        log_experiment(
            agent_name="Fixer",
            model_used="mistral-large-latest",
            action=ActionType.FIX,
            details={
                "input_prompt": f"Fix test failures in {Path(state['file_path']).name} (feedback loop #{state['feedback_loop_count']})",
                "output_response": f"Applied {len(changes)} additional fixes",
                "feedback_loop_count": state["feedback_loop_count"],
                "changes_count": len(changes)
            },
            status="SUCCESS"
        )
        
        return state

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
        """Refactor a single Python file using state-based workflow.
        
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
            log_experiment(
                agent_name="Orchestrator",
                model_used="SYSTEM",
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": f"Read file: {file_path}",
                    "output_response": f"Failed to read file: {str(e)}",
                    "file": file_path
                },
                status="FAILURE"
            )
            return {"status": "error", "error": str(e)}
        
        # Log start of refactoring
        log_experiment(
            agent_name="Orchestrator",
            model_used="SYSTEM",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Start refactoring file: {file_path}",
                "output_response": f"File size: {len(original_code)} bytes",
                "file": file_path,
                "original_size": len(original_code)
            },
            status="SUCCESS"
        )
        
        # Initialize state
        state: RefactoringState = {
            "file_path": file_path,
            "original_code": original_code,
            "current_code": original_code,
            "iteration": 0,
            "issues": [],
            "refactored_code": original_code,
            "changes": [],
            "verdict": "PENDING",
            "feedback": "",
            "tests_passed": False,
            "file_improved": False,
            "error": "",
            "test_code": "",
            "test_error": "",
            "feedback_loop_count": 0
        }
        
        # State machine loop
        print(f"\n[Orchestrator] Starting refactoring workflow for {Path(file_path).name}...")
        
        while state["iteration"] < self.max_iterations:
            # Step 1: Analyze
            state = self._node_analyze(state)
            print(f"[{state['iteration']}] Analyzed: {len(state['issues'])} issues found")
            
            if not state["issues"]:
                state["file_improved"] = True
                break
            
            # Step 2: Apply fixes
            state = self._node_apply_fixes(state)
            if state.get("error"):
                print(f"[{state['iteration']}] Error: {state['error']}")
                break
            
            # Step 3: Validate
            state = self._node_validate(state)
            if state.get("error"):
                print(f"[{state['iteration']}] Validation error: {state['error']}")
                break
            
            # Step 4: Judge
            state = self._node_judge(state)
            print(f"[{state['iteration']}] Judge verdict: {state['verdict']}")
            
            if state["verdict"] != "APPROVED":
                break
            
            # Step 5: Write changes
            state = self._node_write_changes(state)
            print(f"[{state['iteration']}] Changes written")
            
            # Step 6: Run tests
            state = self._node_run_tests(state)
            print(f"[{state['iteration']}] Tests: {'PASSED' if state['tests_passed'] else 'FAILED'}")
            
            # Step 7: Generate unit tests
            state = self._node_generate_tests(state)
            
            # Step 8: Feedback loop for test failures
            if not state["tests_passed"]:
                state = self._node_feedback_loop(state)
                # Continue to next iteration to retry with feedback
                continue
            
            if state["tests_passed"]:
                break
        
        # Log completion
        if state["file_improved"]:
            log_experiment(
                agent_name="Orchestrator",
                model_used="SYSTEM",
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": f"Completed refactoring {Path(file_path).name}",
                    "output_response": f"File improved - iterations: {state['iteration']}",
                    "file": file_path,
                    "iterations": state["iteration"],
                    "final_size": len(state["current_code"])
                },
                status="SUCCESS"
            )
        else:
            log_experiment(
                agent_name="Orchestrator",
                model_used="SYSTEM",
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": f"Refactoring {Path(file_path).name}",
                    "output_response": f"No improvements applied - iterations: {state['iteration']}",
                    "file": file_path,
                    "iterations": state["iteration"],
                    "error": state.get("error", "")
                },
                status="FAILURE"
            )
        
        # Store results
        self.results[file_path] = {
            "iterations": state["iteration"],
            "improved": state["file_improved"],
            "original_size": len(original_code),
            "final_size": len(state["current_code"])
        }
        
        print(f"[Result] {Path(file_path).name}: "
              f"iterations={state['iteration']}, "
              f"improved={state['file_improved']}")
        
        return self.results[file_path]


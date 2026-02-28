#!/usr/bin/env python3
"""Main entry point for the Refactoring Swarm system."""

import argparse
import sys
import os
from dotenv import load_dotenv

from src.orchestrator import Orchestrator
from src.utils.logger import log_experiment, ActionType

# Load environment variables
load_dotenv()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Refactoring Swarm - Agent-based code refactoring system"
    )
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Directory containing Python files to refactor"
    )
    args = parser.parse_args()

    # Validate target directory
    if not os.path.exists(args.target_dir):
        print(f"[ERROR] Directory not found: {args.target_dir}")
        sys.exit(1)

    print(f"\n[STARTUP] Refactoring Swarm initialized")
    print(f"[TARGET] {args.target_dir}\n")

    # Log startup
    log_experiment(
        agent_name="Orchestrator",
        model_used="SYSTEM",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Target directory: {args.target_dir}",
            "output_response": "Orchestrator started"
        },
        status="SUCCESS"
    )

    # Run orchestrator
    try:
        orchestrator = Orchestrator(max_iterations=2)
        results = orchestrator.refactor_directory(args.target_dir)
        
        print(f"\n[RESULTS] Orchestration started for {args.target_dir}")
        print(f"Status: {results.get('status', 'unknown')}")
        print(f"Files discovered: {results.get('files_processed', 0)}")
        
    except Exception as e:
        print(f"[FATAL] Orchestration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
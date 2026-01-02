"""Main entry point for the refactoring swarm system."""

import argparse
import sys

from src.orchestrator import Orchestrator


def main():
    """Parse arguments and initiate orchestration."""
    parser = argparse.ArgumentParser(
        description="Refactoring Swarm - Multi-agent code refactoring system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Target directory for refactoring analysis",
    )
    args = parser.parse_args()

    try:
        orchestrator = Orchestrator(target_dir=args.target_dir)
        result = orchestrator.run()
        
        print(f"Orchestration started for {args.target_dir}")
        print(f"Status: {result['status']}")
        print(f"Files discovered: {result['files_found']}")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
"""Agent definitions for the refactoring swarm.

This module serves as a registry and factory for all agents in the system.
Agents are LangGraph-based components that perform specific refactoring tasks.

Future structure:
- Each agent will be a LangGraph StateGraph
- Agents will be composed into workflows via the orchestrator
- Message passing between agents through state management
"""

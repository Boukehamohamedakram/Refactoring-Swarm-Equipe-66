# Refactoring Swarm – Equipe 66

**Agent-based code refactoring system using Google Gemini API**

## Overview

Refactoring Swarm is an intelligent code refactoring system that uses a multi-agent architecture to analyze, fix, and validate Python code. The system coordinates three specialized agents:

1. **Auditor** - Analyzes code and identifies issues (code quality, performance, security, maintainability)
2. **Fixer** - Applies targeted fixes to identified issues
3. **Judge** - Validates the quality of refactored code

## Architecture

```
src/
├── __init__.py
├── orchestrator.py          # Main orchestration loop
├── agents/
│   ├── __init__.py
│   ├── base_agent.py        # Base class for all agents (API communication, caching, retry logic)
│   ├── auditor.py           # Code analysis agent
│   ├── fixer.py             # Code fixing agent
│   └── judge.py             # Code validation agent
├── prompts/
│   ├── auditor_prompt.txt   # System prompt for auditor
│   ├── fixer_prompt.txt     # System prompt for fixer
│   └── judge_prompt.txt     # System prompt for judge
├── tools/
│   └── __init__.py          # Utility functions (file I/O, syntax validation, test running)
└── utils/
    └── logger.py            # Logging system (logs to logs/experiment_data.json)

main.py                       # Entry point
requirements.txt             # Python dependencies
.env.example                 # Environment variables template
```

## Installation

### Prerequisites
- Python 3.11+
- Google Gemini API key (free tier available at https://aistudio.google.com/apikey)

### Setup

1. **Clone the repository**
```bash
git clone <repository_url>
cd refactoring-swarm-template
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API key**
```bash
cp .env.example .env
# Edit .env and add your Google Gemini API key
```

## Usage

### Basic Refactoring

Refactor a directory of Python files:
```bash
python main.py --target_dir ./path/to/python/files
```

### Example: Refactor the sandbox
```bash
python main.py --target_dir sandbox
```

### Example: Refactor a project
```bash
python main.py --target_dir "C:\Users\user\Projects\my_project"
```

## How It Works

### Workflow

For each Python file discovered:

1. **Auditor Phase**
   - Analyzes code for issues
   - Returns structured JSON with findings
   - Results cached to avoid redundant API calls

2. **Fixer Phase** (if issues found)
   - Receives auditor's issue list
   - Generates refactored code
   - Applies fixes while preserving functionality

3. **Judge Phase**
   - Validates refactored code quality
   - Checks for syntax errors
   - Returns verdict: APPROVED, NEEDS_REVISION, or REJECTED

4. **Testing Phase**
   - Runs pytest to validate functionality
   - Continues iteration if tests pass
   - Max 10 iterations per file

### Features

- **Smart Caching**: Responses cached by model + prompt + content hash to reduce API calls
- **Rate Limiting**: Exponential backoff (5s → 10s → 20s → 60s) for quota exceeded errors
- **Request Throttling**: 2-second delay between API calls to respect rate limits
- **Comprehensive Logging**: All agent interactions logged to `logs/experiment_data.json` for analysis
- **Modular Architecture**: Agents are decoupled and independently testable
- **Configuration Driven**: System prompts loaded from separate files (easy to customize)

## System Prompts

Each agent uses a specialized system prompt stored as plain text:

- **auditor_prompt.txt**: Instructions for identifying code issues
- **fixer_prompt.txt**: Instructions for applying fixes
- **judge_prompt.txt**: Instructions for validating code quality

Prompts are loaded at agent initialization and used for all API calls.

## API Response Handling

The system handles various response formats:

- **JSON Extraction**: Attempts to parse structured JSON responses
- **Error Recovery**: Falls back to error structures if JSON parsing fails
- **Throttling**: Respects API rate limits with exponential backoff
- **Caching**: Stores successful responses to minimize quota usage

## Logging

All agent interactions are logged to `logs/experiment_data.json`:

```json
{
  "id": "unique-uuid",
  "timestamp": "ISO-8601",
  "agent": "Auditor|Fixer|Judge",
  "model": "gemma-3-4b-it",
  "action": "CODE_ANALYSIS|FIX|...",
  "details": {
    "input_prompt": "...",
    "output_response": "...",
    "file": "..."
  },
  "status": "SUCCESS|FAILURE"
}
```

## Configuration

### Models

Current default: `gemma-3-4b-it` (lightweight, fast, lower quota usage)

Alternative: `gemini-2.5-flash` (more powerful, better for complex refactoring)

To change the model, update agent initialization in `src/agents/auditor.py`, `fixer.py`, and `judge.py`:

```python
def __init__(self, model: str = "gemini-2.5-flash"):
```

### Rate Limiting (base_agent.py)

```python
MAX_RETRIES = 3                    # Number of retries on rate limit
INITIAL_BACKOFF = 5                # Initial wait time (seconds)
MAX_BACKOFF = 60                   # Maximum wait time (seconds)
REQUEST_THROTTLE_DELAY = 2         # Min delay between requests (seconds)
```

## Extending the System

### Adding a New Agent

1. Create `src/agents/my_agent.py`:
```python
from src.agents.base_agent import BaseAgent
from src.utils.logger import ActionType

class MyAgent(BaseAgent):
    def __init__(self, model: str = "gemma-3-4b-it"):
        super().__init__(
            agent_name="MyAgent",
            prompt_file="src/prompts/my_agent_prompt.txt",
            model=model
        )
    
    def analyze(self, **kwargs):
        # Implement analysis logic
        pass
```

2. Create `src/prompts/my_agent_prompt.txt` with system instructions

3. Import and use in orchestrator:
```python
from src.agents.my_agent import MyAgent
self.my_agent = MyAgent()
```

### Customizing System Prompts

Edit the `.txt` files in `src/prompts/`:
- Simple text format
- Loaded at agent initialization
- Can include examples and detailed instructions

## Troubleshooting

### 429 RESOURCE_EXHAUSTED Error

**Cause**: Exceeded Google Gemini API quota

**Solutions**:
1. Check quota at https://ai.dev/usage?tab=rate-limit
2. Wait for quota reset
3. Switch to lighter model (`gemma-3-4b-it`)
4. Increase `REQUEST_THROTTLE_DELAY` in base_agent.py

### Python Path Issues

On Windows, use explicit path:
```bash
D:/refactoring-swarm-template/venv/Scripts/python.exe main.py --target_dir sandbox
```

### Import Errors

Ensure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## Performance Notes

- **Caching**: Dramatically reduces API calls (cache hits shown as `[CACHE HIT]`)
- **Throttling**: Prevents rate limiting with 2s delay between requests
- **Iteration**: Default max 10 iterations per file (configurable in Orchestrator)

Typical refactoring of 2 files: 5-10 API calls (with caching)

## Project Structure Summary

| File | Purpose |
|------|---------|
| `main.py` | Entry point, argument parsing |
| `src/orchestrator.py` | Main workflow coordination |
| `src/agents/base_agent.py` | Shared API communication, caching, retry logic |
| `src/agents/auditor.py` | Code analysis |
| `src/agents/fixer.py` | Code refactoring |
| `src/agents/judge.py` | Quality validation |
| `src/tools/__init__.py` | File I/O, syntax validation, test running |
| `src/utils/logger.py` | Structured logging to JSON |
| `src/prompts/*.txt` | System instructions for each agent |

## License

Part of Equipe 66 - Refactoring Swarm project

## Support

For issues or questions, review the logs in `logs/experiment_data.json` for detailed agent interactions.

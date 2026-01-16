"""Base agent class for the refactoring swarm system."""

import hashlib
import json
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

from mistralai import Mistral
from dotenv import load_dotenv

from src.utils.logger import ActionType, log_experiment

# Load environment variables
load_dotenv()

# Get API key from environment
_api_key = os.getenv("MISTRAL_API_KEY")
if not _api_key:
    raise ValueError(
        "MISTRAL_API_KEY not found in environment variables. "
        "Please set it in .env or as an environment variable."
    )

# Initialize Mistral client
_client = Mistral(api_key=_api_key)

# Rate limiting and caching constants
MAX_RETRIES = 3
INITIAL_BACKOFF = 5  # seconds
MAX_BACKOFF = 60  # seconds
REQUEST_THROTTLE_DELAY = 2  # seconds between requests to avoid rate limits
_last_request_time = 0  # Track last API request time for throttling
CACHE_FILE = "logs/api_response_cache.json"

# Global request timestamp for throttling
_last_request_time = 0
_api_response_cache: Dict[str, str] = {}


class BaseAgent(ABC):
    """Base class for all agents in the refactoring swarm."""

    def __init__(self, agent_name: str, prompt_file: str, model: str = "mistral-large-latest"):
        """Initialize the agent.
        
        Args:
            agent_name: Name of the agent (e.g., "Auditor", "Fixer")
            prompt_file: Path to the system prompt file
            model: Mistral model to use
        """
        self.agent_name = agent_name
        self.prompt_file = prompt_file
        self.model_name = model
        self.system_prompt = self._load_prompt()
        self._load_cache()

    def _load_prompt(self) -> str:
        """Load the system prompt from file."""
        with open(self.prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def _load_cache(self):
        """Load API response cache from file."""
        global _api_response_cache
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    _api_response_cache = json.load(f)
            except Exception:
                _api_response_cache = {}

    def _save_cache(self):
        """Save API response cache to file."""
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(_api_response_cache, f, indent=2)
        except Exception as e:
            print(f"[WARN] Failed to save cache: {e}")

    def _get_cache_key(self, user_message: str) -> str:
        """Generate cache key from message."""
        combined = f"{self.model_name}:{self.system_prompt}:{user_message}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _apply_request_throttle(self):
        """Apply request throttling to avoid hitting rate limits."""
        global _last_request_time
        time_since_last_request = time.time() - _last_request_time
        if time_since_last_request < REQUEST_THROTTLE_DELAY:
            wait_time = REQUEST_THROTTLE_DELAY - time_since_last_request
            print(f"[THROTTLE] Waiting {wait_time:.1f}s to respect rate limits")
            time.sleep(wait_time)
        _last_request_time = time.time()

    def call_mistral_api(self, user_message: str) -> str:
        """Call the Mistral API with caching, throttling, and retry logic.
        
        Args:
            user_message: User message to send
            
        Returns:
            API response text (from cache or API)
            
        Raises:
            RuntimeError: If API call fails after retries
        """
        # Load cache at first use
        self._load_cache()
        
        # Check cache first
        cache_key = self._get_cache_key(user_message)
        if cache_key in _api_response_cache:
            print(f"[CACHE HIT] Using cached response (key: {cache_key[:8]}...)")
            return _api_response_cache[cache_key]
        
        # Apply request throttling before API call
        self._apply_request_throttle()
        
        backoff = INITIAL_BACKOFF
        
        for attempt in range(MAX_RETRIES):
            try:
                # Use Mistral client API
                response = _client.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                )
                result = response.choices[0].message.content
                
                # Cache successful response
                _api_response_cache[cache_key] = result
                self._save_cache()
                print(f"[CACHE STORE] Cached new response (key: {cache_key[:8]}...)")
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # Check for rate limit errors
                if "429" in error_msg or "rate" in error_msg.lower() or "quota" in error_msg.lower():
                    if attempt < MAX_RETRIES - 1:
                        wait_time = min(backoff, MAX_BACKOFF)
                        print(f"[RATE_LIMITED] Waiting {wait_time}s before retry {attempt + 1}/{MAX_RETRIES}")
                        time.sleep(wait_time)
                        backoff *= 2  # Exponential backoff
                        continue
                
                # For other errors or final attempt, raise
                raise RuntimeError(f"Mistral API call failed: {error_msg}")
        
        raise RuntimeError("Mistral API call failed: Max retries exceeded")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from API.
        
        Args:
            response: Raw API response
            
        Returns:
            Parsed JSON dictionary
        """
        # Try to extract JSON from response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                try:
                    return json.loads(response[start:end+1])
                except json.JSONDecodeError:
                    pass
            # If all else fails, return error structure
            return {"error": "Failed to parse JSON response", "raw_response": response}

    def log_interaction(self, action: ActionType, details: dict, status: str):
        """Log an agent interaction to the experiment log.
        
        Args:
            action: Type of action performed
            details: Details dictionary (must include input_prompt and output_response)
            status: SUCCESS or FAILURE
        """
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=action,
            details=details,
            status=status
        )

    @abstractmethod
    def analyze(self, **kwargs) -> Dict[str, Any]:
        """Analyze code - must be implemented by subclasses."""
        pass

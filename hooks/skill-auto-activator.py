#!/usr/bin/env python3
"""
Skill Auto-Activator Hook for Claude Code.
Analyzes user prompts and suggests relevant superpowers skills.
Runs on UserPromptSubmit event.
"""

import json
import sys
import re
import logging
from pathlib import Path
from typing import Optional, List, Tuple

# Setup logging
LOG_DIR = Path.home() / ".claude" / "hooks" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "skill-auto-activator.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Pre-compiled patterns with word boundaries for safety
SKILL_PATTERNS: List[Tuple[re.Pattern, str]] = [
    # Debugging & Investigation
    (re.compile(r"\b(bug|error|fix|broken|failing|crash|exception)\b", re.IGNORECASE),
     "superpowers:systematic-debugging"),
    (re.compile(r"\b(trace|backtrace|stack|origin)\b", re.IGNORECASE),
     "superpowers:root-cause-tracing"),

    # Design & Planning
    (re.compile(r"\b(brainstorm|idea|concept|design|think\s+through)\b", re.IGNORECASE),
     "superpowers:brainstorming"),
    (re.compile(r"\b(plan|roadmap|strategy|approach|architect)\b", re.IGNORECASE),
     "superpowers:write-plan"),

    # Development
    (re.compile(r"\b(implement|add|create|build|develop)\s+(feature|functionality|component)\b", re.IGNORECASE),
     "superpowers:test-driven-development"),
    (re.compile(r"\b(test|tdd|spec|unit\s+test)\b", re.IGNORECASE),
     "superpowers:test-driven-development"),
    (re.compile(r"\b(refactor|clean|improve)\s+code\b", re.IGNORECASE),
     "superpowers:requesting-code-review"),

    # Testing Issues
    (re.compile(r"\b(flaky|intermittent|race\s*condition|timing)\b", re.IGNORECASE),
     "superpowers:condition-based-waiting"),
    (re.compile(r"\b(mock|stub|fake|test\s+double)\b", re.IGNORECASE),
     "superpowers:testing-anti-patterns"),

    # Parallel & Scale
    (re.compile(r"\b(parallel|concurrent|multiple)\s+(task|agent|investigation)\b", re.IGNORECASE),
     "superpowers:dispatching-parallel-agents"),
    (re.compile(r"\b(worktree|isolated|branch\s+work)\b", re.IGNORECASE),
     "superpowers:using-git-worktrees"),

    # Review & Completion
    (re.compile(r"\b(review|check|verify)\s+(code|changes|implementation)\b", re.IGNORECASE),
     "superpowers:requesting-code-review"),
    (re.compile(r"\b(complete|done|finish|merge|pr|pull\s*request)\b", re.IGNORECASE),
     "superpowers:verification-before-completion"),

    # Validation
    (re.compile(r"\b(valid|sanitize|check\s+input|boundary)\b", re.IGNORECASE),
     "superpowers:defense-in-depth"),
]

# Maximum input length to prevent ReDoS
MAX_INPUT_LENGTH = 10000


def suggest_skill(prompt: str) -> Optional[str]:
    """
    Match prompt against skill rules and return best match.

    Args:
        prompt: User's input prompt

    Returns:
        Skill name if matched, None otherwise
    """
    # Truncate to prevent ReDoS attacks
    if len(prompt) > MAX_INPUT_LENGTH:
        logger.warning(f"Prompt truncated from {len(prompt)} to {MAX_INPUT_LENGTH}")
        prompt = prompt[:MAX_INPUT_LENGTH]

    for pattern, skill in SKILL_PATTERNS:
        try:
            if pattern.search(prompt):
                logger.debug(f"Matched pattern for skill: {skill}")
                return skill
        except re.error as e:
            logger.error(f"Regex error for skill {skill}: {e}")
            continue

    return None


def safe_get_string(data: dict, key: str, default: str = "") -> str:
    """Safely extract string value from dict."""
    value = data.get(key, default)
    if value is None:
        return default
    return str(value)


def main() -> None:
    """Main hook entry point."""
    try:
        # Read input with size limit
        raw_input = sys.stdin.read(MAX_INPUT_LENGTH * 2)
        input_data = json.loads(raw_input)

        prompt = safe_get_string(input_data, "prompt", "")
        logger.info(f"Processing prompt of length {len(prompt)}")

        suggested = suggest_skill(prompt)

        if suggested:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"Suggested skill: {suggested}\nConsider using the Skill tool to invoke it for this task."
                }
            }
            print(json.dumps(output))
            logger.info(f"Suggested skill: {suggested}")

        sys.exit(0)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        sys.exit(0)
    except KeyError as e:
        logger.error(f"Missing key: {e}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
RIPER Phase Validator Hook for Claude Code.
Validates that tool usage aligns with current RIPER phase.
Runs on PreToolUse event.

RIPER Phases:
- Research: Read-only investigation (Grep, Glob, Read, WebSearch)
- Innovate: Read-only design exploration (same as Research)
- Plan: Read + Memory (Write only to memory-bank/)
- Execute: Full access (all tools)
- Review: Read + Test (Bash for tests, Read, Grep)
"""

import json
import sys
import os
import logging
from pathlib import Path
from typing import Tuple, Optional, Set, Dict, Any

# Setup logging
LOG_DIR = Path.home() / ".claude" / "hooks" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "riper-phase-validator.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Tools allowed in each phase
PHASE_ALLOWED_TOOLS: Dict[str, Optional[Set[str]]] = {
    "research": {"Read", "Grep", "Glob", "WebSearch", "WebFetch", "Task"},
    "innovate": {"Read", "Grep", "Glob", "WebSearch", "WebFetch", "Task", "AskUserQuestion"},
    "plan": {"Read", "Grep", "Glob", "WebSearch", "WebFetch", "Task", "Write", "Edit", "AskUserQuestion"},
    "execute": None,  # None means all tools allowed
    "review": {"Read", "Grep", "Glob", "Bash", "Task", "AskUserQuestion"},
}


def get_current_phase() -> str:
    """
    Determine current RIPER phase from environment or session state.
    Defaults to 'execute' (most permissive) if not set.

    Returns:
        Current phase name (lowercase)
    """
    # Check environment variable first
    phase = os.environ.get("RIPER_PHASE", "").lower().strip()

    if phase in PHASE_ALLOWED_TOOLS:
        logger.debug(f"Phase from env: {phase}")
        return phase

    # Check session file if exists
    session_file = Path.home() / ".claude" / "memory-bank" / "current-session.json"
    if session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session = json.load(f)
                phase = str(session.get("riper_phase", "execute")).lower().strip()
                if phase in PHASE_ALLOWED_TOOLS:
                    logger.debug(f"Phase from session file: {phase}")
                    return phase
        except (json.JSONDecodeError, PermissionError, OSError) as e:
            logger.warning(f"Could not read session file: {e}")

    logger.debug("Defaulting to execute phase")
    return "execute"


def validate_tool(
    tool_name: str,
    phase: str,
    tool_input: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """
    Check if tool is allowed in current phase.

    Args:
        tool_name: Name of the tool being invoked
        phase: Current RIPER phase
        tool_input: Optional tool parameters for additional validation

    Returns:
        Tuple of (is_valid, error_message)
    """
    allowed = PHASE_ALLOWED_TOOLS.get(phase)

    # Execute phase allows everything
    if allowed is None:
        return True, ""

    if tool_name not in allowed:
        return False, f"Tool '{tool_name}' not allowed in {phase.upper()} phase. Allowed: {', '.join(sorted(allowed))}"

    # Special validation for plan phase writes
    if phase == "plan" and tool_name in {"Write", "Edit"}:
        if tool_input:
            file_path = str(tool_input.get("file_path", ""))
            if file_path and "memory-bank" not in file_path:
                return False, f"PLAN phase writes must target memory-bank/ directory. Got: {file_path}"

    return True, ""


def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """Safely get value from dict with type checking."""
    try:
        return data.get(key, default)
    except (AttributeError, TypeError):
        return default


def main() -> None:
    """Main hook entry point."""
    try:
        input_data = json.load(sys.stdin)

        tool_name = str(safe_get(input_data, "tool_name", ""))
        tool_input = safe_get(input_data, "tool_input", {})

        if not isinstance(tool_input, dict):
            tool_input = {}

        logger.info(f"Validating tool: {tool_name}")

        current_phase = get_current_phase()
        is_valid, message = validate_tool(tool_name, current_phase, tool_input)

        if not is_valid:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": f"RIPER Phase Warning: {message}"
                }
            }
            print(json.dumps(output))
            logger.warning(f"Validation failed: {message}")

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

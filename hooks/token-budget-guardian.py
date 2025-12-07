#!/usr/bin/env python3
"""
Token Budget Guardian Hook for Claude Code.
Monitors and warns about token usage to prevent runaway consumption.
Runs on PreToolUse and Stop events.
"""

import json
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Setup logging
LOG_DIR = Path.home() / ".claude" / "hooks" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "token-budget-guardian.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "sessionBudget": int(os.environ.get("TOKEN_BUDGET", 200000)),
    "singleCallWarn": 10000,
    "cumulativeWarnPercent": 0.75,
    "summaryThreshold": 50000,
}

# Token estimates per tool (rough approximations)
TOOL_TOKEN_ESTIMATES: Dict[str, int] = {
    "Read": 500,
    "Write": 200,
    "Edit": 300,
    "Glob": 100,
    "Grep": 200,
    "Bash": 500,
    "Task": 5000,
    "WebSearch": 1000,
    "WebFetch": 2000,
}

# Session tracking file
SESSION_FILE = Path.home() / ".claude" / "hooks" / "session-tokens.json"


def load_session() -> Dict[str, Any]:
    """Load current session token tracking."""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"total_tokens": 0, "tool_calls": 0, "started": datetime.now().isoformat()}


def save_session(session: Dict[str, Any]) -> None:
    """Save session token tracking."""
    try:
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)
    except IOError as e:
        logger.error(f"Could not save session: {e}")


def estimate_tokens(tool_name: str, tool_input: Optional[Dict] = None) -> int:
    """
    Estimate tokens for a tool call.

    Args:
        tool_name: Name of the tool
        tool_input: Tool input parameters

    Returns:
        Estimated token count
    """
    base = TOOL_TOKEN_ESTIMATES.get(tool_name, 200)

    if tool_input:
        # Adjust for content size
        if "content" in tool_input:
            content_len = len(str(tool_input.get("content", "")))
            base += content_len // 4  # ~4 chars per token

        if "prompt" in tool_input:
            prompt_len = len(str(tool_input.get("prompt", "")))
            base += prompt_len // 4

    return base


def check_budget(
    session: Dict[str, Any],
    estimated_tokens: int
) -> tuple[str, Optional[str]]:
    """
    Check if tool call is within budget.

    Args:
        session: Current session data
        estimated_tokens: Estimated tokens for this call

    Returns:
        Tuple of (action, message)
    """
    total = session.get("total_tokens", 0)
    projected = total + estimated_tokens
    budget = CONFIG["sessionBudget"]
    percent_used = projected / budget

    # Check single call warning
    if estimated_tokens > CONFIG["singleCallWarn"]:
        return "warn", f"Large operation: ~{estimated_tokens:,} tokens. Session total will be {percent_used:.0%} of budget."

    # Check cumulative warning
    if percent_used > CONFIG["cumulativeWarnPercent"] and percent_used < 1.0:
        msg = f"Token budget at {percent_used:.0%}. Consider context compression."
        if total > CONFIG["summaryThreshold"]:
            msg += " Suggest using context-curator agent."
        return "warn", msg

    # Hard stop at budget
    if percent_used >= 1.0:
        return "block", f"Session token budget ({budget:,}) exhausted. Archive session and start fresh."

    return "allow", None


def main() -> None:
    """Main hook entry point."""
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")

        # Load session tracking
        session = load_session()

        # Estimate tokens for this call
        tool_input = input_data.get("tool_input", {})
        if not isinstance(tool_input, dict):
            tool_input = {}

        estimated = estimate_tokens(tool_name, tool_input)

        # Check budget
        action, message = check_budget(session, estimated)

        if action == "block":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": f"BUDGET EXCEEDED: {message}"
                }
            }
            print(json.dumps(output))
            logger.warning(f"Budget exceeded: {message}")
            sys.exit(2)

        elif action == "warn":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": f"Token Budget: {message}"
                }
            }
            print(json.dumps(output))
            logger.info(f"Budget warning: {message}")

        # Update session tracking
        session["total_tokens"] = session.get("total_tokens", 0) + estimated
        session["tool_calls"] = session.get("tool_calls", 0) + 1
        session["last_tool"] = tool_name
        session["last_updated"] = datetime.now().isoformat()
        save_session(session)

        sys.exit(0)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()

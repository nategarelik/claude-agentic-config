#!/usr/bin/env python3
"""
Git Safety Net Hook for Claude Code.
Prevents dangerous git operations that could cause data loss.
Runs on PreToolUse event for Bash commands.
"""

import json
import sys
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional

# Setup logging
LOG_DIR = Path.home() / ".claude" / "hooks" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "git-safety-net.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Patterns that are ALWAYS blocked
ALWAYS_BLOCK: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"git\s+push.*--force.*(?:main|master)", re.IGNORECASE),
     "Force push to main/master is extremely dangerous"),
    (re.compile(r"rm\s+-rf?\s+\.git\b", re.IGNORECASE),
     "Deleting .git directory destroys repository history"),
    (re.compile(r"git\s+push.*-f.*origin\s+(?:main|master)", re.IGNORECASE),
     "Force push to main/master is extremely dangerous"),
]

# Patterns that require confirmation
DANGEROUS_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    (re.compile(r"git\s+push\s+(?:-f|--force)", re.IGNORECASE),
     "Force push can overwrite remote history",
     "Use `git push --force-with-lease` for safer force push"),

    (re.compile(r"git\s+reset\s+--hard", re.IGNORECASE),
     "Hard reset discards all uncommitted changes",
     "Consider `git stash` to save changes, or `git reset --soft` to keep changes staged"),

    (re.compile(r"git\s+clean\s+-fd", re.IGNORECASE),
     "Clean with -fd removes untracked files and directories permanently",
     "Run `git clean -n` first to preview what will be deleted"),

    (re.compile(r"git\s+checkout\s+--\s+\.", re.IGNORECASE),
     "Checkout -- . discards all uncommitted changes in working directory",
     "Consider `git stash` to save changes first"),

    (re.compile(r"git\s+stash\s+drop", re.IGNORECASE),
     "Stash drop permanently deletes stashed changes",
     "Verify stash content with `git stash show -p` before dropping"),

    (re.compile(r"git\s+branch\s+-D", re.IGNORECASE),
     "Branch -D force deletes branch even if not merged",
     "Use `git branch -d` (lowercase) for safe deletion that checks merge status"),

    (re.compile(r"git\s+rebase(?!\s+--abort)", re.IGNORECASE),
     "Rebase rewrites commit history",
     "Create backup branch first: `git branch backup-before-rebase`"),
]


def check_command(command: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Check if command is a dangerous git operation.

    Args:
        command: The bash command to check

    Returns:
        Tuple of (action, message, suggestion)
        action: "allow", "warn", or "block"
    """
    # Check absolute blocks first
    for pattern, reason in ALWAYS_BLOCK:
        if pattern.search(command):
            logger.warning(f"BLOCKED: {command} - {reason}")
            return "block", reason, None

    # Check dangerous patterns
    for pattern, warning, suggestion in DANGEROUS_PATTERNS:
        if pattern.search(command):
            logger.info(f"WARNING: {command} - {warning}")
            return "warn", warning, suggestion

    return "allow", None, None


def main() -> None:
    """Main hook entry point."""
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")

        # Only check Bash commands
        if tool_name != "Bash":
            sys.exit(0)

        tool_input = input_data.get("tool_input", {})
        if not isinstance(tool_input, dict):
            sys.exit(0)

        command = tool_input.get("command", "")
        if not command:
            sys.exit(0)

        logger.info(f"Checking command: {command[:100]}...")

        action, message, suggestion = check_command(command)

        if action == "block":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": f"BLOCKED: {message}\n\nThis operation could cause irreversible data loss. If you need to perform this operation, run it manually in the terminal with full understanding of the consequences."
                }
            }
            print(json.dumps(output))
            sys.exit(2)  # Exit code 2 blocks the tool

        elif action == "warn":
            context = f"WARNING: {message}"
            if suggestion:
                context += f"\n\nSafer alternative: {suggestion}"

            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": context
                }
            }
            print(json.dumps(output))

        sys.exit(0)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()

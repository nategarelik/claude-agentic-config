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
from pathlib import Path
from typing import Tuple

# Tools allowed in each phase
PHASE_ALLOWED_TOOLS = {
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
    """
    # Check environment variable first
    phase = os.environ.get("RIPER_PHASE", "").lower()

    if phase in PHASE_ALLOWED_TOOLS:
        return phase

    # Check session file if exists
    session_file = Path.home() / ".claude" / "memory-bank" / "current-session.json"
    if session_file.exists():
        try:
            with open(session_file, "r") as f:
                session = json.load(f)
                phase = session.get("riper_phase", "execute").lower()
                if phase in PHASE_ALLOWED_TOOLS:
                    return phase
        except:
            pass

    return "execute"  # Default to most permissive

def validate_tool(tool_name: str, phase: str) -> Tuple[bool, str]:
    """Check if tool is allowed in current phase."""
    allowed = PHASE_ALLOWED_TOOLS.get(phase)

    # Execute phase allows everything
    if allowed is None:
        return True, ""

    if tool_name in allowed:
        return True, ""

    return False, f"Tool '{tool_name}' not allowed in {phase.upper()} phase. Allowed: {', '.join(sorted(allowed))}"

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")

        current_phase = get_current_phase()
        is_valid, message = validate_tool(tool_name, current_phase)

        if not is_valid:
            # Provide warning but don't block (soft enforcement)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": f"RIPER Phase Warning: {message}"
                }
            }
            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Silent failure
        sys.exit(0)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Session Archiver Hook for Claude Code.
Archives session context to memory-bank when session stops.
Runs on Stop event.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

def get_memory_bank_path() -> Path:
    """Get path to memory bank directory."""
    return Path.home() / ".claude" / "memory-bank" / "main" / "sessions"

def archive_session(session_data: dict) -> str:
    """Archive session data to memory bank."""
    memory_path = get_memory_bank_path()
    memory_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_file = memory_path / f"session_{timestamp}.json"

    archive_data = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_data.get("session_id", "unknown"),
        "summary": session_data.get("summary", ""),
        "tools_used": session_data.get("tools_used", []),
        "files_modified": session_data.get("files_modified", []),
        "key_decisions": session_data.get("key_decisions", []),
    }

    with open(archive_file, "w") as f:
        json.dump(archive_data, f, indent=2)

    return str(archive_file)

def main():
    try:
        input_data = json.load(sys.stdin)

        # Extract session info from stop event
        session_data = {
            "session_id": input_data.get("session_id", ""),
            "summary": input_data.get("summary", "Session ended"),
            "tools_used": input_data.get("tools_used", []),
            "files_modified": input_data.get("files_modified", []),
            "key_decisions": input_data.get("key_decisions", []),
        }

        archive_file = archive_session(session_data)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": f"Session archived to: {archive_file}"
            }
        }
        print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Silent failure - don't block session end
        sys.exit(0)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Session Archiver Hook for Claude Code.
Archives session context to memory-bank when session stops.
Runs on Stop event.
"""

import json
import sys
import os
import logging
import tempfile
import shutil
import uuid
import re
from datetime import datetime
from pathlib import Path
from typing import Any, List

# Setup logging
LOG_DIR = Path.home() / ".claude" / "hooks" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "session-archiver.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_memory_bank_path() -> Path:
    """Get path to memory bank directory."""
    return Path.home() / ".claude" / "memory-bank" / "main" / "sessions"


def sanitize_filename(filename: str) -> str:
    """
    Remove dangerous characters from filename.

    Args:
        filename: Raw filename string

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove path separators and special chars
    safe = re.sub(r'[^\w\-_.]', '_', str(filename))
    # Prevent directory traversal
    safe = safe.replace('..', '_')
    # Limit length
    return safe[:100]


def safe_get_string(data: dict, key: str, default: str = "") -> str:
    """Safely extract string value from dict."""
    value = data.get(key, default)
    if value is None:
        return default
    return str(value)[:10000]  # Limit length


def safe_get_list(data: dict, key: str) -> List[Any]:
    """Safely extract list value from dict."""
    value = data.get(key, [])
    if isinstance(value, list):
        return value[:1000]  # Limit items
    return []


def check_disk_space(path: Path, required_mb: int = 5) -> bool:
    """
    Check if sufficient disk space available.

    Args:
        path: Path to check
        required_mb: Minimum required MB

    Returns:
        True if sufficient space available
    """
    try:
        stat = shutil.disk_usage(path)
        available_mb = stat.free / (1024 * 1024)
        return available_mb >= required_mb
    except (OSError, AttributeError):
        return True  # Assume OK if can't check


def archive_session(session_data: dict) -> str:
    """
    Archive session data to memory bank with atomic write.

    Args:
        session_data: Session information to archive

    Returns:
        Path to archive file

    Raises:
        IOError: If disk space insufficient
        OSError: If write fails
    """
    memory_path = get_memory_bank_path()
    memory_path.mkdir(parents=True, exist_ok=True)

    # Check disk space
    if not check_disk_space(memory_path):
        raise IOError("Insufficient disk space for session archive")

    # Generate unique filename (prevent collision)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    archive_file = memory_path / f"session_{timestamp}_{unique_id}.json"

    archive_data = {
        "timestamp": datetime.now().isoformat(),
        "session_id": sanitize_filename(session_data.get("session_id", "unknown")),
        "summary": safe_get_string(session_data, "summary", "Session ended"),
        "tools_used": safe_get_list(session_data, "tools_used"),
        "files_modified": safe_get_list(session_data, "files_modified"),
        "key_decisions": safe_get_list(session_data, "key_decisions"),
    }

    # Atomic write via temp file
    temp_fd = None
    temp_path = None
    try:
        temp_fd, temp_path = tempfile.mkstemp(
            dir=memory_path,
            prefix=".session_",
            suffix=".tmp"
        )

        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        temp_fd = None  # Prevent double-close

        # Atomic rename
        shutil.move(temp_path, archive_file)
        logger.info(f"Session archived to: {archive_file}")
        return str(archive_file)

    except Exception as e:
        # Clean up temp file on failure
        if temp_path and Path(temp_path).exists():
            try:
                os.unlink(temp_path)
            except OSError:
                pass
        raise


def main() -> None:
    """Main hook entry point."""
    try:
        input_data = json.load(sys.stdin)

        # Extract session info from stop event with validation
        session_data = {
            "session_id": safe_get_string(input_data, "session_id", "unknown"),
            "summary": safe_get_string(input_data, "summary", "Session ended"),
            "tools_used": safe_get_list(input_data, "tools_used"),
            "files_modified": safe_get_list(input_data, "files_modified"),
            "key_decisions": safe_get_list(input_data, "key_decisions"),
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

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        sys.exit(0)
    except IOError as e:
        logger.error(f"IO error: {e}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()

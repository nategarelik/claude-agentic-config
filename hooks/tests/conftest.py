"""
Pytest configuration and fixtures for hook tests.
"""

import pytest
import json
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_stdin(monkeypatch):
    """Factory fixture to mock stdin with JSON data."""
    import io
    import sys

    def _mock_stdin(data: dict):
        json_str = json.dumps(data)
        monkeypatch.setattr(sys, 'stdin', io.StringIO(json_str))

    return _mock_stdin


@pytest.fixture
def sample_prompt_input():
    """Sample UserPromptSubmit input."""
    return {"prompt": "Help me fix a bug in my code"}


@pytest.fixture
def sample_tool_input():
    """Sample PreToolUse input."""
    return {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/path/to/file.py",
            "content": "print('hello')"
        }
    }


@pytest.fixture
def sample_stop_input():
    """Sample Stop event input."""
    return {
        "session_id": "test-session-123",
        "summary": "Implemented feature X",
        "tools_used": ["Read", "Write", "Bash"],
        "files_modified": ["/path/to/file.py"],
        "key_decisions": ["Used factory pattern"]
    }


@pytest.fixture
def sample_subagent_output():
    """Sample SubagentStop input."""
    return {
        "agent_name": "code-review-sentinel",
        "output": """
# Code Review Report

## verdict: PASS

## files_reviewed
- src/main.py
- src/utils.py

## Summary
Code looks good with minor suggestions.
"""
    }

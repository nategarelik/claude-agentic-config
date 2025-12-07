# Creating Hooks

This guide explains how to create custom hooks for the Claude Agentic Config.

## Hook Overview

Hooks are Python scripts that run at specific events during Claude Code execution.

## Hook Events

| Event | When It Fires | Use Case |
|-------|---------------|----------|
| `UserPromptSubmit` | User sends a message | Input validation, suggestions |
| `PreToolUse` | Before tool execution | Permission checks, safety gates |
| `PostToolUse` | After tool execution | Logging, side effects |
| `SubagentStop` | Subagent completes | Quality validation |
| `Stop` | Main agent stops | Session archival, cleanup |

## Basic Structure

```python
#!/usr/bin/env python3
"""
Hook Name - Brief description.
Triggers: EventName
"""

import json
import sys
from typing import Optional

def main() -> None:
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        # Process the event
        result = process(input_data)

        # Output result (if any)
        if result:
            print(json.dumps(result))

        sys.exit(0)

    except Exception as e:
        # Log error but don't block
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(0)

def process(data: dict) -> Optional[dict]:
    """Process the hook event."""
    # Your logic here
    return None

if __name__ == "__main__":
    main()
```

## Input Format

Each event provides different data:

### UserPromptSubmit
```json
{
  "prompt": "user's message text"
}
```

### PreToolUse
```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file",
    "content": "..."
  }
}
```

### PostToolUse
```json
{
  "tool_name": "Write",
  "tool_input": {...},
  "tool_output": "Tool result..."
}
```

### SubagentStop
```json
{
  "agent_name": "code-review-sentinel",
  "output": "Agent's response..."
}
```

### Stop
```json
{
  "session_id": "abc123",
  "summary": "Session summary..."
}
```

## Output Format

Return JSON with `hookSpecificOutput`:

```python
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": "Message to show in Claude Code"
    }
}
```

### Blocking a Tool

For PreToolUse, exit with code 2 to block:
```python
if dangerous_operation:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "Blocked: This operation is not allowed"
        }
    }))
    sys.exit(2)  # Exit code 2 = block
```

## Example: File Size Validator

```python
#!/usr/bin/env python3
"""
File Size Validator - Prevents writing files larger than limit.
Triggers: PreToolUse (Write, Edit)
"""

import json
import sys
from typing import Optional

MAX_FILE_SIZE = 100_000  # 100KB

def main() -> None:
    try:
        input_data = json.load(sys.stdin)
        result = validate(input_data)

        if result:
            print(json.dumps(result))
            if result.get("block"):
                sys.exit(2)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)  # Invalid input, allow
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(0)

def validate(data: dict) -> Optional[dict]:
    """Check file size before write."""
    tool_name = data.get("tool_name", "")

    if tool_name not in ("Write", "Edit"):
        return None

    tool_input = data.get("tool_input", {})
    content = tool_input.get("content", "")

    if len(content) > MAX_FILE_SIZE:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": f"Blocked: File size ({len(content)} bytes) exceeds limit ({MAX_FILE_SIZE} bytes)"
            },
            "block": True
        }

    return None

if __name__ == "__main__":
    main()
```

## Registering Hooks

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"~/.claude/hooks/file-size-validator.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### Matcher Patterns

- Exact match: `"Write"`
- Multiple tools: `"Write|Edit|Bash"`
- All tools: `"*"`
- Regex: `"Notebook.*"`

## Best Practices

### Error Handling
Always catch exceptions and exit cleanly:
```python
except Exception as e:
    # Log but don't block
    sys.exit(0)
```

### Timeouts
Hooks have timeouts (default 60s). Keep processing fast:
```python
# Bad: Long-running operation
result = expensive_api_call()

# Good: Quick local check
result = check_local_cache()
```

### Encoding
Always specify UTF-8:
```python
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
```

### Logging
Write debug info to a log file:
```python
import logging
from pathlib import Path

log_file = Path.home() / ".claude" / "hooks" / "logs" / "my-hook.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG)
```

### Type Hints
Add type hints for clarity:
```python
def process(data: dict) -> Optional[dict]:
    ...
```

## Testing Hooks

### Manual Test
```bash
echo '{"tool_name": "Write", "tool_input": {"content": "test"}}' | python hooks/my-hook.py
```

### Unit Tests
Create `hooks/tests/test_my_hook.py`:
```python
import pytest
from my_hook import validate

def test_allows_small_files():
    result = validate({
        "tool_name": "Write",
        "tool_input": {"content": "small"}
    })
    assert result is None

def test_blocks_large_files():
    result = validate({
        "tool_name": "Write",
        "tool_input": {"content": "x" * 200_000}
    })
    assert result["block"] is True
```

### Run Tests
```bash
pytest hooks/tests/ -v
```

## Common Patterns

### Rate Limiting
```python
import time
from pathlib import Path

RATE_LIMIT_FILE = Path.home() / ".claude" / "hooks" / ".rate_limit"
COOLDOWN_SECONDS = 5

def check_rate_limit() -> bool:
    if RATE_LIMIT_FILE.exists():
        last_call = float(RATE_LIMIT_FILE.read_text())
        if time.time() - last_call < COOLDOWN_SECONDS:
            return False
    RATE_LIMIT_FILE.write_text(str(time.time()))
    return True
```

### Caching
```python
import json
from pathlib import Path
from hashlib import md5

CACHE_DIR = Path.home() / ".claude" / "hooks" / "cache"

def get_cached(key: str) -> Optional[dict]:
    cache_file = CACHE_DIR / f"{md5(key.encode()).hexdigest()}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    return None
```

### Metrics
```python
import json
from datetime import datetime
from pathlib import Path

METRICS_FILE = Path.home() / ".claude" / "hooks" / "metrics.jsonl"

def log_metric(hook_name: str, duration_ms: float):
    metric = {
        "hook": hook_name,
        "duration_ms": duration_ms,
        "timestamp": datetime.now().isoformat()
    }
    with open(METRICS_FILE, "a") as f:
        f.write(json.dumps(metric) + "\n")
```

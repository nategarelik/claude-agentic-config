#!/usr/bin/env python3
"""
Output Quality Gate Hook for Claude Code.
Validates agent output quality before accepting.
Runs on SubagentStop event.
"""

import json
import sys
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Setup logging
LOG_DIR = Path.home() / ".claude" / "hooks" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "output-quality-gate.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Quality rules
CONFIG = {
    "minResponseLength": 50,
    "maxCodeBlockWithoutExplanation": 100,
}

# Required sections per agent type
REQUIRED_SECTIONS: Dict[str, List[str]] = {
    "code-review-sentinel": ["verdict", "files_reviewed"],
    "context-curator": ["Active State", "Key Decisions"],
    "dependency-auditor": ["Risk Score", "Summary"],
}

# Anti-patterns to flag
ANTI_PATTERNS: List[re.Pattern] = [
    re.compile(r"I don't know", re.IGNORECASE),
    re.compile(r"I cannot help", re.IGNORECASE),
    re.compile(r"As an AI", re.IGNORECASE),
    re.compile(r"I apologize, but", re.IGNORECASE),
    re.compile(r"I'm not able to", re.IGNORECASE),
]


def check_quality(agent_name: str, output: str) -> List[Dict[str, Any]]:
    """
    Check output quality and return list of issues.

    Args:
        agent_name: Name of the agent that produced output
        output: The agent's output text

    Returns:
        List of issue dictionaries
    """
    issues = []

    # Check minimum length
    if len(output) < CONFIG["minResponseLength"]:
        issues.append({
            "severity": "HIGH",
            "issue": "Response too brief",
            "suggestion": "Expand with specific details and examples"
        })

    # Check required sections for known agents
    required = REQUIRED_SECTIONS.get(agent_name, [])
    for section in required:
        if section not in output:
            issues.append({
                "severity": "MEDIUM",
                "issue": f"Missing required section: {section}",
                "suggestion": f"Add {section} section to output"
            })

    # Check for anti-patterns
    for pattern in ANTI_PATTERNS:
        if pattern.search(output):
            issues.append({
                "severity": "LOW",
                "issue": "Contains hedging/deflection language",
                "suggestion": "Replace with direct, actionable content"
            })
            break  # Only flag once

    # Check for large unexplained code blocks
    code_blocks = re.findall(r"```[\s\S]*?```", output)
    for block in code_blocks:
        lines = block.count('\n') + 1
        if lines > CONFIG["maxCodeBlockWithoutExplanation"]:
            # Check if there's explanation nearby
            block_index = output.find(block)
            surrounding = output[max(0, block_index - 200):block_index]
            surrounding += output[block_index + len(block):block_index + len(block) + 200]

            if len(surrounding.strip()) < 50:
                issues.append({
                    "severity": "MEDIUM",
                    "issue": f"Large code block ({lines} lines) without explanation",
                    "suggestion": "Add context explaining what the code does and why"
                })

    return issues


def format_issues(issues: List[Dict[str, Any]]) -> str:
    """Format issues for display."""
    lines = ["Output Quality Issues:"]
    for issue in issues:
        severity = issue["severity"]
        msg = issue["issue"]
        suggestion = issue.get("suggestion", "")
        lines.append(f"  [{severity}] {msg}")
        if suggestion:
            lines.append(f"         Suggestion: {suggestion}")
    return "\n".join(lines)


def main() -> None:
    """Main hook entry point."""
    try:
        input_data = json.load(sys.stdin)

        agent_name = input_data.get("agent_name", "unknown")
        output = input_data.get("output", "")

        if not output:
            logger.warning("Empty output received")
            sys.exit(0)

        logger.info(f"Checking quality for agent: {agent_name}")

        issues = check_quality(agent_name, output)

        if not issues:
            logger.info("Quality check passed")
            sys.exit(0)

        # Determine action based on severity
        has_high = any(i["severity"] == "HIGH" for i in issues)

        if has_high:
            output_msg = {
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStop",
                    "additionalContext": format_issues(issues) + "\n\nConsider regenerating with more detail."
                }
            }
            print(json.dumps(output_msg))
            logger.warning(f"Quality check failed: {len(issues)} issues")
        else:
            output_msg = {
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStop",
                    "additionalContext": format_issues(issues)
                }
            }
            print(json.dumps(output_msg))
            logger.info(f"Quality check passed with {len(issues)} warnings")

        sys.exit(0)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()

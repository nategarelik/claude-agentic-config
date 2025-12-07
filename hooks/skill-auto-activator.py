#!/usr/bin/env python3
"""
Skill Auto-Activator Hook for Claude Code.
Analyzes user prompts and suggests relevant superpowers skills.
Runs on UserPromptSubmit event.
"""

import json
import sys
import re
from typing import Optional

SKILL_RULES = {
    # Debugging & Investigation
    r"(bug|error|fix|broken|failing|crash|exception)": "superpowers:systematic-debugging",
    r"(trace|backtrace|stack|origin|source\s+of)": "superpowers:root-cause-tracing",

    # Design & Planning
    r"(brainstorm|idea|concept|design|think\s+through)": "superpowers:brainstorming",
    r"(plan|roadmap|strategy|approach|architect)": "superpowers:write-plan",

    # Development
    r"(implement|add|create|build|develop)\s+(feature|functionality|component)": "superpowers:test-driven-development",
    r"(test|tdd|spec|unit\s+test)": "superpowers:test-driven-development",
    r"(refactor|clean|improve)\s+code": "superpowers:requesting-code-review",

    # Testing Issues
    r"(flaky|intermittent|race\s*condition|timing)": "superpowers:condition-based-waiting",
    r"(mock|stub|fake|test\s+double)": "superpowers:testing-anti-patterns",

    # Parallel & Scale
    r"(parallel|concurrent|multiple)\s+(task|agent|investigation)": "superpowers:dispatching-parallel-agents",
    r"(worktree|isolated|branch\s+work)": "superpowers:using-git-worktrees",

    # Review & Completion
    r"(review|check|verify)\s+(code|changes|implementation)": "superpowers:requesting-code-review",
    r"(complete|done|finish|merge|pr|pull\s*request)": "superpowers:verification-before-completion",

    # Validation
    r"(valid|sanitize|check\s+input|boundary)": "superpowers:defense-in-depth",
}

def suggest_skill(prompt: str) -> Optional[str]:
    """Match prompt against skill rules and return best match."""
    prompt_lower = prompt.lower()

    for pattern, skill in SKILL_RULES.items():
        if re.search(pattern, prompt_lower):
            return skill

    return None

def main():
    try:
        input_data = json.load(sys.stdin)
        prompt = input_data.get("prompt", "")

        suggested = suggest_skill(prompt)

        if suggested:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"Suggested skill: {suggested}\nConsider using the Skill tool to invoke it for this task."
                }
            }
            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        # Silent failure - don't block user workflow
        sys.exit(0)

if __name__ == "__main__":
    main()

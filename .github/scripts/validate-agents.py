#!/usr/bin/env python3
"""
Validate agent markdown files have proper YAML frontmatter.
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML not installed, skipping validation")
    sys.exit(0)


def validate_agent_file(agent_file: Path) -> list:
    """Validate agent file structure and return errors."""
    errors = []
    content = agent_file.read_text(encoding="utf-8")

    # Check for YAML frontmatter
    if not content.startswith("---"):
        errors.append(f"{agent_file.name}: Missing YAML frontmatter")
        return errors

    # Extract and validate YAML
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{agent_file.name}: Invalid frontmatter structure")
        return errors

    try:
        metadata = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        errors.append(f"{agent_file.name}: Invalid YAML - {e}")
        return errors

    if metadata is None:
        errors.append(f"{agent_file.name}: Empty frontmatter")
        return errors

    # Validate required fields
    required = ["name", "description", "tools", "model"]
    for field in required:
        if field not in metadata:
            errors.append(f"{agent_file.name}: Missing required field '{field}'")

    # Validate tools is list
    if "tools" in metadata and not isinstance(metadata["tools"], list):
        errors.append(f"{agent_file.name}: 'tools' must be a list")

    # Validate model is valid
    valid_models = ["opus", "sonnet", "haiku"]
    if "model" in metadata and metadata["model"] not in valid_models:
        errors.append(f"{agent_file.name}: Invalid model '{metadata['model']}', must be one of {valid_models}")

    return errors


def main():
    """Validate all agent files."""
    agents_dir = Path("agents")

    if not agents_dir.exists():
        print("No agents directory found")
        sys.exit(0)

    all_errors = []

    for agent_file in agents_dir.glob("*.md"):
        print(f"Validating {agent_file.name}...")
        errors = validate_agent_file(agent_file)
        all_errors.extend(errors)

    if all_errors:
        print("\nAgent validation errors:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\nAll agent files valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()

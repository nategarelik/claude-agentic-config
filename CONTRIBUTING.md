# Contributing to Claude Agentic Config

Thank you for your interest in contributing! This document provides guidelines for contributions.

## Types of Contributions

### Accepted
- Bug fixes in hooks or agents
- New agents with clear use cases
- New hooks that improve workflow
- Documentation improvements
- Test coverage expansion
- Performance optimizations

### Please Discuss First
- Major architectural changes
- New dependencies
- Changes to core workflow patterns

## Getting Started

### Prerequisites
- Python 3.9+
- Git
- Claude Code CLI

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/nategarelik/claude-agentic-config.git
cd claude-agentic-config

# Install development dependencies
pip install -r hooks/requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest hooks/tests/ -v
```

## Development Workflow

### 1. Create an Issue First

Before starting work, create an issue describing:
- What you want to change
- Why it's needed
- Proposed approach

### 2. Branch Naming

```
feature/add-new-agent-name
fix/hook-error-handling
docs/improve-getting-started
```

### 3. Make Changes

Follow these standards:

**For Python hooks:**
- Add type hints to all functions
- Include docstrings with examples
- Handle exceptions specifically (no bare `except:`)
- Add tests for new functionality
- Run `ruff check` and `mypy` before committing

**For agent markdown:**
- Include complete YAML frontmatter (name, description, tools, model)
- Document when to use the agent
- Provide example workflows
- Keep under 500 lines (use references/ for details)

**For documentation:**
- Use clear, concise language
- Include code examples
- Update table of contents if needed

### 4. Testing

```bash
# Run all tests
pytest hooks/tests/ -v

# Run with coverage
pytest hooks/tests/ --cov=hooks --cov-report=term

# Type checking
mypy hooks/*.py --ignore-missing-imports

# Linting
ruff check hooks/
```

### 5. Commit Messages

Format:
```
type(scope): brief description

Longer explanation if needed.

Closes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

Examples:
```
feat(agents): add dependency-auditor agent
fix(hooks): handle JSON decode errors in session-archiver
docs(readme): add installation troubleshooting
```

### 6. Pull Request

- Fill out the PR template completely
- Link related issues
- Ensure CI passes
- Request review from maintainers

## Code Style

### Python

```python
# Good
def validate_tool(tool_name: str, phase: str) -> tuple[bool, str]:
    """
    Validate tool usage against RIPER phase.

    Args:
        tool_name: Name of the tool being invoked
        phase: Current RIPER phase

    Returns:
        Tuple of (is_valid, error_message)
    """
    if phase not in VALID_PHASES:
        return False, f"Unknown phase: {phase}"
    # ...

# Bad
def validate_tool(tool, p):
    if p not in VALID_PHASES:
        return False, "bad phase"
```

### Agent Markdown

```markdown
---
name: agent-name
description: Clear one-line description of purpose
model: sonnet
tools:
  - Read
  - Grep
  - Glob
---

# Agent Name

Brief overview (2-3 sentences).

## When to Use

- Specific scenario 1
- Specific scenario 2

## Process

### Step 1: Name
Description of step.

### Step 2: Name
Description of step.

## Output Format

Describe expected output structure.
```

## Quality Standards

### Agents Must Have
- [ ] Clear, specific purpose (not generic)
- [ ] Defined tool permissions
- [ ] Documented use cases
- [ ] Example workflows
- [ ] Error handling guidance

### Hooks Must Have
- [ ] Specific exception handling
- [ ] Input validation
- [ ] Timeout consideration
- [ ] Logging for debugging
- [ ] At least 80% test coverage

## Getting Help

- Open an issue for questions
- Check existing issues and docs first
- Be specific about your environment and problem

## Recognition

Contributors are recognized in:
- Release notes
- README acknowledgments
- Git commit history

Thank you for contributing!

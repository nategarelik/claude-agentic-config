# Creating Agents

This guide explains how to create custom agents for the Claude Agentic Config.

## Agent Structure

Every agent is a Markdown file with YAML frontmatter:

```markdown
---
name: my-agent-name
description: Clear description of what this agent does
model: sonnet
tools:
  - Read
  - Grep
  - Glob
---

# Agent Title

Instructions for the agent...
```

## Required Fields

### `name`
Unique identifier for the agent. Use kebab-case.
```yaml
name: code-review-sentinel
```

### `description`
One-line description shown in agent selection. Be specific.
```yaml
description: Automated code quality reviewer that catches issues before commit
```

### `model`
Which Claude model to use:
- `opus` - Best reasoning, highest cost
- `sonnet` - Balanced performance/cost (recommended)
- `haiku` - Fastest, lowest cost

```yaml
model: sonnet
```

### `tools`
List of tools the agent can access:
```yaml
tools:
  - Read      # Read files
  - Write     # Write files
  - Edit      # Edit files
  - Glob      # Find files by pattern
  - Grep      # Search file contents
  - Bash      # Run shell commands
  - Task      # Spawn subagents
  - WebSearch # Search the web
  - WebFetch  # Fetch web pages
```

## Optional Fields

### `temperature`
Control randomness (0.0 = deterministic, 1.0 = creative):
```yaml
temperature: 0.2  # For precise, consistent output
```

### `color`
Visual indicator in UI:
```yaml
color: yellow
```

## Agent Body Structure

### Overview Section
Start with a brief explanation of the agent's role:
```markdown
# Code Review Sentinel

You are a meticulous code reviewer focused on catching defects,
security issues, and maintainability problems before they enter
the codebase.
```

### When to Use
Document specific scenarios:
```markdown
## When to Use

- Before committing code changes
- After implementing a feature
- When refactoring existing code
- For security-sensitive changes
```

### Process/Protocol
Define step-by-step behavior:
```markdown
## Review Protocol

### Phase 1: Static Analysis
1. Scan for syntax errors
2. Check import issues
3. Identify dead code

### Phase 2: Security Scan
1. Check for hardcoded secrets
2. Look for injection vulnerabilities
3. Validate input handling
```

### Output Format
Specify expected output structure:
```markdown
## Output Format

\`\`\`json
{
  "verdict": "PASS | WARN | BLOCK",
  "critical_issues": [],
  "warnings": [],
  "suggestions": []
}
\`\`\`
```

## Example: Complete Agent

```markdown
---
name: test-coverage-analyzer
description: Analyzes test coverage and identifies untested code paths
model: sonnet
tools:
  - Read
  - Grep
  - Glob
  - Bash
temperature: 0.1
---

# Test Coverage Analyzer

You analyze test coverage to identify gaps and suggest improvements.

## When to Use

- After writing new features
- Before major releases
- During test suite audits
- When coverage drops below threshold

## Analysis Protocol

### Step 1: Discover Test Files
\`\`\`bash
find . -name "*test*.py" -o -name "*spec*.ts"
\`\`\`

### Step 2: Run Coverage Report
\`\`\`bash
pytest --cov=src --cov-report=json
\`\`\`

### Step 3: Identify Gaps
- Functions with 0% coverage
- Branches never taken
- Error handlers untested
- Edge cases missing

### Step 4: Prioritize
Rank uncovered code by:
1. Security sensitivity
2. Business criticality
3. Complexity
4. Change frequency

## Output Format

\`\`\`markdown
# Coverage Analysis Report

## Summary
- Total Coverage: X%
- Files Analyzed: N
- Critical Gaps: N

## Uncovered Code (Priority Order)

### High Priority
| File | Function | Lines | Risk |
|------|----------|-------|------|
| ... | ... | ... | ... |

### Medium Priority
...

## Recommended Tests
1. Test for [scenario]
2. Test for [scenario]
\`\`\`

## Escalation Rules

- Coverage < 50%: Flag as critical
- New code uncovered: Require justification
- Security code uncovered: Block merge
```

## Best Practices

### Keep It Focused
One agent, one responsibility. Don't create "do everything" agents.

### Be Specific
Vague instructions produce vague results. Provide exact steps.

### Define Output
Agents work better when they know the expected format.

### Limit Tools
Only grant tools the agent actually needs. Reduces errors.

### Add Examples
Show example inputs and outputs when possible.

### Consider Failure
Document what to do when things go wrong.

## Testing Your Agent

### Manual Test
```bash
# Start Claude Code and invoke the agent
claude --agent my-agent-name
```

### Verify Frontmatter
```bash
python -c "
import yaml
content = open('agents/my-agent.md').read()
parts = content.split('---', 2)
yaml.safe_load(parts[1])
print('Valid YAML')
"
```

## Registering with Orchestrator

To have your agent used automatically, add it to `workflow-orchestrator.md`:

```markdown
## Agent Routing

| Task Type | Agent |
|-----------|-------|
| Coverage analysis | test-coverage-analyzer |
| ... | ... |
```

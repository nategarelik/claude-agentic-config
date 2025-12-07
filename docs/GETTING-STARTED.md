# Getting Started

This guide walks you through setting up and using the Claude Agentic Config.

## Prerequisites

- Claude Code CLI installed
- Python 3.9 or higher
- Git (for version control features)

## Installation

### Quick Install

**Unix/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/nategarelik/claude-agentic-config/main/scripts/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://raw.githubusercontent.com/nategarelik/claude-agentic-config/main/scripts/install.ps1 | iex
```

### Manual Install

1. **Backup existing config** (if any):
   ```bash
   mv ~/.claude ~/.claude.backup
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/nategarelik/claude-agentic-config.git ~/.claude
   ```

3. **Verify installation:**
   ```bash
   ls ~/.claude/agents/
   ls ~/.claude/hooks/
   ```

4. **Restart Claude Code** to load the new configuration.

## First Steps

### 1. Verify Hooks Are Working

Test the skill auto-activator:
```bash
echo '{"prompt": "fix a bug in my code"}' | python ~/.claude/hooks/skill-auto-activator.py
```

Expected output:
```json
{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "Suggested skill: superpowers:systematic-debugging..."}}
```

### 2. Understand RIPER Phases

The system uses RIPER workflow phases:

| Phase | What You Do | What's Allowed |
|-------|-------------|----------------|
| **Research** | Investigate the problem | Read files, search, browse |
| **Innovate** | Brainstorm solutions | Same as Research + design discussions |
| **Plan** | Create implementation plan | Write to memory-bank/ only |
| **Execute** | Write code | Full access to all tools |
| **Review** | Validate work | Read, test, review |

Set your phase with environment variable:
```bash
export RIPER_PHASE=research
```

### 3. Try a Workflow

Start Claude Code and try:

```
Help me implement user authentication for my API
```

The workflow orchestrator will guide you through:
1. Brainstorming approach
2. Planning implementation
3. Executing with TDD
4. Reviewing the code

## Core Workflows

### Feature Development

```
You: "Add a dark mode toggle to the settings page"

Claude will:
1. Brainstorm UI patterns and state management
2. Create implementation plan
3. Implement with tests
4. Review code quality
5. Verify completion
```

### Bug Fixing

```
You: "There's a bug where users can't log out"

Claude will:
1. Investigate systematically
2. Trace to root cause
3. Write regression test
4. Fix the bug
5. Verify the fix
```

### Code Review

```
You: "Review my changes before I commit"

Claude will:
1. Analyze all modified files
2. Check for security issues
3. Evaluate code quality
4. Suggest improvements
5. Provide verdict (PASS/WARN/BLOCK)
```

## Configuration

### Adjusting Token Budget

Edit `~/.claude/hooks/token-budget-guardian.py`:
```python
CONFIG = {
    "sessionBudget": 200000,  # Increase for longer sessions
    "singleCallWarn": 10000,
    # ...
}
```

### Disabling a Hook

Comment out in `~/.claude/settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      // {
      //   "hooks": [...]
      // }
    ]
  }
}
```

### Adding Custom Skills

The skill-auto-activator can suggest your custom skills. Edit the `SKILL_RULES` in `skill-auto-activator.py`:
```python
SKILL_RULES = {
    r"(my-keyword)": "my-custom-skill",
    # ... existing rules
}
```

## Troubleshooting

### Hooks Not Running

1. Check hook path exists:
   ```bash
   ls ~/.claude/hooks/skill-auto-activator.py
   ```

2. Verify Python is accessible:
   ```bash
   python --version
   ```

3. Check settings.json syntax:
   ```bash
   python -m json.tool ~/.claude/settings.json
   ```

### Agent Not Found

1. Verify agent file exists:
   ```bash
   ls ~/.claude/agents/
   ```

2. Check YAML frontmatter is valid:
   ```bash
   head -20 ~/.claude/agents/workflow-orchestrator.md
   ```

### Session Archives Missing

1. Check memory-bank directory:
   ```bash
   ls ~/.claude/memory-bank/main/sessions/
   ```

2. Verify write permissions:
   ```bash
   touch ~/.claude/memory-bank/main/sessions/test.txt
   ```

## Next Steps

- Read [Architecture Overview](ARCHITECTURE.md) for system design
- Learn [Creating Agents](guides/creating-agents.md) to add custom agents
- Explore [Creating Hooks](guides/creating-hooks.md) for automation
- See [Workflow Guide](guides/workflows.md) for advanced patterns

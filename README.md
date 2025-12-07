# Claude Agentic Config

A professional-grade agentic system configuration for Claude Code, featuring RIPER workflows, specialized agents, automated hooks, and comprehensive quality gates.

## Features

- **RIPER Workflow** - Phase-separated development (Research, Innovate, Plan, Execute, Review)
- **6 Specialist Agents** - Orchestration, code review, context management, dependency auditing
- **6 Automated Hooks** - Skill suggestions, phase validation, quality gates, git safety
- **Memory Bank** - Persistent context across sessions
- **Quality Gates** - Automated code review, output validation, token budgeting

## Quick Start

### Installation

**Option 1: Clone directly**
```bash
git clone https://github.com/nategarelik/claude-agentic-config.git ~/.claude
```

**Option 2: Run installer**
```bash
# Unix/macOS
curl -fsSL https://raw.githubusercontent.com/nategarelik/claude-agentic-config/main/scripts/install.sh | bash

# Windows PowerShell
irm https://raw.githubusercontent.com/nategarelik/claude-agentic-config/main/scripts/install.ps1 | iex
```

**Option 3: Manual setup**
1. Clone or download this repository
2. Copy contents to `~/.claude/`
3. Restart Claude Code

### Verify Installation

```bash
# Check hooks are configured
cat ~/.claude/settings.json | grep hooks

# Test a hook
echo '{"prompt": "fix bug"}' | python ~/.claude/hooks/skill-auto-activator.py
```

## Components

### Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| `workflow-orchestrator` | Routes tasks to appropriate skills/workflows | opus |
| `code-review-sentinel` | Automated code quality review | sonnet |
| `context-curator` | Manages and compresses session context | sonnet |
| `dependency-auditor` | Security and health analysis of dependencies | sonnet |
| `plugin-capability-scout` | Discovers plugins and MCP servers | sonnet |
| `agentic-system-architect` | Designs multi-agent systems | opus |

### Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `skill-auto-activator` | UserPromptSubmit | Suggests relevant superpowers skills |
| `riper-phase-validator` | PreToolUse | Enforces RIPER phase constraints |
| `session-archiver` | Stop | Archives session to memory bank |
| `token-budget-guardian` | PreToolUse | Monitors and limits token usage |
| `output-quality-gate` | SubagentStop | Validates output quality |
| `git-safety-net` | PreToolUse | Prevents dangerous git operations |

## Workflows

### Standard Feature Development
```
1. brainstorming        -> Refine requirements
2. write-plan           -> Create implementation plan
3. test-driven-dev      -> Implement with TDD
4. code-review          -> Automated review
5. verify-completion    -> Final verification
```

### Bug Investigation
```
1. systematic-debugging -> Investigate root cause
2. root-cause-tracing   -> Trace to source
3. test-driven-dev      -> Write regression test
4. verify-completion    -> Confirm fix
```

### RIPER Phases

| Phase | Mode | Allowed Actions |
|-------|------|-----------------|
| Research | Read-only | Grep, Glob, Read, WebSearch |
| Innovate | Read-only | + Brainstorming, design exploration |
| Plan | Read + Memory | + Write to memory-bank/ |
| Execute | Full access | All tools |
| Review | Read + Test | Run tests, code review |

## Configuration

### Settings

Edit `~/.claude/settings.json` to customize:

```json
{
  "hooks": {
    "UserPromptSubmit": [...],
    "PreToolUse": [...],
    "Stop": [...]
  }
}
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `RIPER_PHASE` | Override current RIPER phase | `execute` |
| `TOKEN_BUDGET` | Session token limit | `200000` |
| `HOOK_LOG_LEVEL` | Hook logging verbosity | `INFO` |

## Directory Structure

```
~/.claude/
├── agents/                 # Specialist agent definitions
│   ├── workflow-orchestrator.md
│   ├── code-review-sentinel.md
│   └── ...
├── hooks/                  # Automated hook scripts
│   ├── skill-auto-activator.py
│   ├── riper-phase-validator.py
│   └── tests/              # Hook test suite
├── docs/                   # Documentation
│   ├── guides/             # How-to guides
│   └── reference/          # API reference
├── memory-bank/            # Persistent context
│   └── main/
│       ├── plans/
│       ├── reviews/
│       ├── sessions/
│       └── decisions/
├── scripts/                # Installation scripts
├── CLAUDE.md               # Token-optimized instructions
└── settings.json           # Hook configuration
```

## Documentation

- [Getting Started](docs/GETTING-STARTED.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Creating Agents](docs/guides/creating-agents.md)
- [Creating Hooks](docs/guides/creating-hooks.md)
- [Workflow Guide](docs/guides/workflows.md)
- [Agent Reference](docs/reference/agents.md)
- [Hook Reference](docs/reference/hooks.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [Claude Code](https://claude.ai/code)
- Inspired by [superpowers-marketplace](https://github.com/anthropics/superpowers-marketplace)
- Uses patterns from RIPER workflow and AB Method

# Architecture Overview

This document describes the architecture of the Claude Agentic Config system.

## System Design

```
                    ┌─────────────────────────────────────┐
                    │           User Request              │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │     UserPromptSubmit Hook Chain     │
                    │  ┌─────────────────────────────┐    │
                    │  │   skill-auto-activator.py   │    │
                    │  └─────────────────────────────┘    │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │       Workflow Orchestrator         │
                    │   (Routes to appropriate agents)    │
                    └─────────────────┬───────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
           ▼                          ▼                          ▼
    ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
    │   Agent 1    │          │   Agent 2    │          │   Agent N    │
    └──────┬───────┘          └──────┬───────┘          └──────┬───────┘
           │                          │                          │
           └──────────────────────────┼──────────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │       PreToolUse Hook Chain         │
                    │  ┌─────────────────────────────┐    │
                    │  │  riper-phase-validator.py   │    │
                    │  │  token-budget-guardian.py   │    │
                    │  │     git-safety-net.py       │    │
                    │  └─────────────────────────────┘    │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │          Tool Execution             │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │      SubagentStop Hook Chain        │
                    │  ┌─────────────────────────────┐    │
                    │  │   output-quality-gate.py    │    │
                    │  └─────────────────────────────┘    │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────▼───────────────────┐
                    │           Stop Hook Chain           │
                    │  ┌─────────────────────────────┐    │
                    │  │    session-archiver.py      │    │
                    │  └─────────────────────────────┘    │
                    └─────────────────────────────────────┘
```

## Core Concepts

### RIPER Workflow

The system enforces phase-separated development:

| Phase | Purpose | Constraints |
|-------|---------|-------------|
| **Research** | Understand the problem | Read-only operations |
| **Innovate** | Explore solutions | Read-only + brainstorming |
| **Plan** | Design approach | Write only to memory-bank/ |
| **Execute** | Implement solution | Full tool access |
| **Review** | Validate work | Read + test operations |

### Agent Composition

Agents are composed using these patterns:

**Sequential Delegation**
```
Agent1 → Agent2 → Agent3 → Output
```
Use for staged processing (brainstorm → plan → execute → review).

**Parallel Investigation**
```
Primary → [Agent1, Agent2, Agent3] → Aggregator
```
Use for independent problem analysis.

**Feedback Loop**
```
Agent → Review → Pass/Fail → Refinement/Completion
```
Use for iterative improvement (code review → fix → re-review).

### Hook Chain

Hooks execute at specific events:

1. **UserPromptSubmit** - Before processing user input
2. **PreToolUse** - Before each tool invocation
3. **PostToolUse** - After tool completion
4. **SubagentStop** - When subagent completes
5. **Stop** - When main agent stops

### Memory Bank

Persistent context stored in `~/.claude/memory-bank/`:

```
memory-bank/
├── main/
│   ├── plans/      # Implementation specifications
│   ├── reviews/    # Code review reports
│   ├── sessions/   # Archived session contexts
│   └── decisions/  # Architecture Decision Records
└── [branch]/       # Branch-specific context
```

## Agent Catalog

### Orchestration Layer

| Agent | Role | Tools |
|-------|------|-------|
| `workflow-orchestrator` | Routes tasks to skills | All |

### Quality Layer

| Agent | Role | Tools |
|-------|------|-------|
| `code-review-sentinel` | Code quality review | Read, Grep, Glob |
| `output-quality-gate` | Output validation | Read |

### Context Layer

| Agent | Role | Tools |
|-------|------|-------|
| `context-curator` | Context compression | Read, Write, Glob |
| `session-archiver` | Session persistence | Write |

### Analysis Layer

| Agent | Role | Tools |
|-------|------|-------|
| `dependency-auditor` | Dependency analysis | Read, Bash, WebSearch |
| `plugin-capability-scout` | Plugin discovery | WebSearch, Read |

### Design Layer

| Agent | Role | Tools |
|-------|------|-------|
| `agentic-system-architect` | System design | Read, Task |

## Hook Catalog

### Input Processing

| Hook | Event | Purpose |
|------|-------|---------|
| `skill-auto-activator` | UserPromptSubmit | Suggest skills |

### Safety & Validation

| Hook | Event | Purpose |
|------|-------|---------|
| `riper-phase-validator` | PreToolUse | Enforce phases |
| `git-safety-net` | PreToolUse | Block dangerous git ops |
| `token-budget-guardian` | PreToolUse | Monitor tokens |

### Quality Assurance

| Hook | Event | Purpose |
|------|-------|---------|
| `output-quality-gate` | SubagentStop | Validate output |

### Session Management

| Hook | Event | Purpose |
|------|-------|---------|
| `session-archiver` | Stop | Archive context |

## Design Decisions

### ADR-001: Hook Language Choice

**Decision:** Python for all hooks

**Rationale:**
- Cross-platform compatibility
- Rich standard library
- Easy JSON handling
- Familiar to most developers

### ADR-002: Agent Model Selection

**Decision:** Sonnet for most agents, Opus for orchestration

**Rationale:**
- Sonnet: Fast, cost-effective for focused tasks
- Opus: Superior reasoning for complex routing

### ADR-003: No Subagent-to-Subagent Communication

**Decision:** Main agent coordinates all subagents

**Rationale:**
- Prevents cascade complexity
- Clearer debugging
- Predictable execution flow

## Extension Points

### Adding New Agents

1. Create `agents/my-agent.md` with YAML frontmatter
2. Define tools, model, and instructions
3. Register in workflow-orchestrator if needed

### Adding New Hooks

1. Create `hooks/my-hook.py` following the template
2. Add to `settings.json` with appropriate event
3. Add tests in `hooks/tests/`

### Custom Workflows

1. Define workflow in `docs/guides/`
2. Create supporting agents if needed
3. Update orchestrator routing

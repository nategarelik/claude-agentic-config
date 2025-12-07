# Claude Code Instructions

## System Overview

This configuration implements an enhanced agentic system with:
- **RIPER Workflow**: Phase-separated development (Research → Innovate → Plan → Execute → Review)
- **AB Method**: Mission-based task decomposition
- **Superpowers Skills**: Automated skill suggestions and workflows
- **Memory Bank**: Persistent context across sessions

## Quick Reference

### Workflow Patterns

| Task Type | Workflow |
|-----------|----------|
| New Feature | brainstorm → write-plan → TDD/subagent-dev → code-review → verify |
| Bug Fix | systematic-debugging → root-cause-tracing → TDD → verify |
| Flaky Tests | condition-based-waiting → testing-anti-patterns → verify |
| Multi-Issue | dispatching-parallel-agents → aggregate → plan → execute |

### RIPER Phases

| Phase | Mode | Allowed Actions |
|-------|------|-----------------|
| Research | Read-only | Grep, Glob, Read, WebSearch |
| Innovate | Read-only | + Brainstorming, design exploration |
| Plan | Read + Memory | + Write to memory-bank/plans/ |
| Execute | Full access | All tools, subagent delegation |
| Review | Read + Test | Run tests, code review |

## Agents Available

See `.claude/agents/` for specialist agents:
- `workflow-orchestrator`: Routes tasks to skills/workflows
- `plugin-capability-scout`: Discovers and integrates capabilities
- `agentic-system-architect`: Designs multi-agent systems

## Memory Bank Structure

```
.claude/memory-bank/
├── main/
│   ├── plans/      # Implementation specifications
│   ├── reviews/    # Code review reports
│   ├── sessions/   # Archived session contexts
│   └── decisions/  # ADRs and decisions
└── [branch]/       # Branch-specific context
```

## Key Principles

1. **Brainstorm before coding** - Design clarity prevents rework
2. **Test-first development** - Write test, see it fail, make it pass
3. **Verify before completion** - Evidence before assertions
4. **No subagent spawning subagents** - Main agent coordinates all
5. **Use read-only phases** - Prevent premature implementation

## Hook System

Hooks run automatically:
- **UserPromptSubmit**: Suggests relevant skills for your task
- **PreToolUse**: Validates tool usage against RIPER phase
- **Stop**: Archives session to memory bank

## Resources

- Superpowers Plugin: `/skill superpowers:using-superpowers`
- Claude Code Docs: `/skill superpowers-developing-for-claude-code:working-with-claude-code`
- Plugin Discovery: Use `plugin-capability-scout` agent

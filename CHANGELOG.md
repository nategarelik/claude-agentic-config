# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-06

### Added
- **New Agents**
  - `code-review-sentinel` - Automated code quality reviewer
  - `context-curator` - Session context management and compression
  - `dependency-auditor` - Dependency security and health analysis

- **New Hooks**
  - `token-budget-guardian` - Token usage monitoring and limits
  - `output-quality-gate` - Output validation for agents
  - `git-safety-net` - Prevents dangerous git operations

- **Documentation**
  - Comprehensive README with quick start
  - Architecture documentation
  - Agent and hook guides
  - API reference documentation

- **Quality**
  - Test suite for all hooks
  - CI/CD with GitHub Actions
  - Pre-commit hooks for code quality
  - Type hints throughout Python code

- **Infrastructure**
  - Installation scripts (Unix/Windows)
  - Plugin manifest for marketplace compatibility
  - Logging infrastructure for debugging

### Changed
- Improved error handling in all hooks (specific exceptions)
- Added UTF-8 encoding to all file operations
- Atomic writes in session-archiver
- ReDoS protection in skill-auto-activator

### Fixed
- Bare exception catching replaced with specific handlers
- File encoding issues on Windows
- Timestamp collision in session archives
- Path traversal vulnerability in session-archiver

## [1.0.0] - 2024-12-06

### Added
- Initial release
- **Agents**
  - `workflow-orchestrator` - Task routing and coordination
  - `plugin-capability-scout` - Plugin discovery
  - `agentic-system-architect` - System design

- **Hooks**
  - `skill-auto-activator` - Skill suggestions
  - `riper-phase-validator` - RIPER workflow enforcement
  - `session-archiver` - Session persistence

- **Features**
  - RIPER workflow support
  - Memory bank structure
  - Basic CLAUDE.md configuration

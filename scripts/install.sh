#!/bin/bash
#
# Claude Agentic Config Installer (Unix/macOS)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/nategarelik/claude-agentic-config/main/scripts/install.sh | bash
#

set -e

REPO_URL="https://github.com/nategarelik/claude-agentic-config.git"
INSTALL_DIR="$HOME/.claude"
BACKUP_DIR="$HOME/.claude-backup-$(date +%Y%m%d_%H%M%S)"

echo "==================================="
echo " Claude Agentic Config Installer"
echo "==================================="
echo ""

# Check for git
if ! command -v git &> /dev/null; then
    echo "Error: git is required but not installed."
    echo "Please install git and try again."
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Warning: Python 3 not found. Hooks may not work."
fi

# Backup existing config
if [ -d "$INSTALL_DIR" ]; then
    echo "Backing up existing configuration to $BACKUP_DIR..."
    mv "$INSTALL_DIR" "$BACKUP_DIR"
    echo "Backup complete."
fi

# Clone repository
echo ""
echo "Installing Claude Agentic Config..."
git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"

# Remove .git to avoid nested repo issues (optional)
# rm -rf "$INSTALL_DIR/.git"

# Create logs directory
mkdir -p "$INSTALL_DIR/hooks/logs"

# Make hooks executable
chmod +x "$INSTALL_DIR/hooks/"*.py 2>/dev/null || true

# Verify installation
echo ""
echo "Verifying installation..."

if [ -f "$INSTALL_DIR/settings.json" ]; then
    echo "  [OK] settings.json"
else
    echo "  [FAIL] settings.json not found"
fi

if [ -d "$INSTALL_DIR/agents" ]; then
    echo "  [OK] agents directory"
else
    echo "  [FAIL] agents directory not found"
fi

if [ -d "$INSTALL_DIR/hooks" ]; then
    echo "  [OK] hooks directory"
else
    echo "  [FAIL] hooks directory not found"
fi

# Test a hook
if command -v python3 &> /dev/null; then
    echo ""
    echo "Testing hooks..."
    echo '{"prompt": "test"}' | python3 "$INSTALL_DIR/hooks/skill-auto-activator.py" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "  [OK] Hooks are working"
    else
        echo "  [WARN] Hook test failed"
    fi
fi

echo ""
echo "==================================="
echo " Installation Complete!"
echo "==================================="
echo ""
echo "Restart Claude Code to load the new configuration."
echo ""
echo "What's included:"
echo "  - 6 specialist agents"
echo "  - 6 automated hooks"
echo "  - RIPER workflow support"
echo "  - Memory bank structure"
echo ""
echo "Documentation: $INSTALL_DIR/README.md"
echo ""

if [ -d "$BACKUP_DIR" ]; then
    echo "Your previous configuration was backed up to:"
    echo "  $BACKUP_DIR"
    echo ""
fi

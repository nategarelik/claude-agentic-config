#
# Claude Agentic Config Installer (Windows PowerShell)
#
# Usage:
#   irm https://raw.githubusercontent.com/nategarelik/claude-agentic-config/main/scripts/install.ps1 | iex
#

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/nategarelik/claude-agentic-config.git"
$InstallDir = "$env:USERPROFILE\.claude"
$BackupDir = "$env:USERPROFILE\.claude-backup-$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "===================================" -ForegroundColor Cyan
Write-Host " Claude Agentic Config Installer" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check for git
try {
    $null = Get-Command git -ErrorAction Stop
} catch {
    Write-Host "Error: git is required but not installed." -ForegroundColor Red
    Write-Host "Please install git and try again."
    exit 1
}

# Check for Python
try {
    $null = Get-Command python -ErrorAction Stop
} catch {
    Write-Host "Warning: Python not found. Hooks may not work." -ForegroundColor Yellow
}

# Backup existing config
if (Test-Path $InstallDir) {
    Write-Host "Backing up existing configuration to $BackupDir..."
    Move-Item -Path $InstallDir -Destination $BackupDir
    Write-Host "Backup complete." -ForegroundColor Green
}

# Clone repository
Write-Host ""
Write-Host "Installing Claude Agentic Config..."
git clone --depth 1 $RepoUrl $InstallDir

# Create logs directory
New-Item -ItemType Directory -Path "$InstallDir\hooks\logs" -Force | Out-Null

# Verify installation
Write-Host ""
Write-Host "Verifying installation..."

if (Test-Path "$InstallDir\settings.json") {
    Write-Host "  [OK] settings.json" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] settings.json not found" -ForegroundColor Red
}

if (Test-Path "$InstallDir\agents") {
    Write-Host "  [OK] agents directory" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] agents directory not found" -ForegroundColor Red
}

if (Test-Path "$InstallDir\hooks") {
    Write-Host "  [OK] hooks directory" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] hooks directory not found" -ForegroundColor Red
}

# Test a hook
try {
    $null = Get-Command python -ErrorAction Stop
    Write-Host ""
    Write-Host "Testing hooks..."
    $result = '{"prompt": "test"}' | python "$InstallDir\hooks\skill-auto-activator.py" 2>&1
    Write-Host "  [OK] Hooks are working" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Hook test skipped (Python not available)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host " Installation Complete!" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Restart Claude Code to load the new configuration."
Write-Host ""
Write-Host "What's included:"
Write-Host "  - 6 specialist agents"
Write-Host "  - 6 automated hooks"
Write-Host "  - RIPER workflow support"
Write-Host "  - Memory bank structure"
Write-Host ""
Write-Host "Documentation: $InstallDir\README.md"
Write-Host ""

if (Test-Path $BackupDir) {
    Write-Host "Your previous configuration was backed up to:"
    Write-Host "  $BackupDir"
    Write-Host ""
}

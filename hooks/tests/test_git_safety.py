"""
Tests for git-safety-net hook.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def git_safety():
    """Import the git safety module."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "git_safety",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "git-safety-net.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGitSafetyBlocking:
    """Test commands that should be blocked."""

    def test_blocks_force_push_main(self, git_safety):
        """Should block force push to main."""
        action, msg, _ = git_safety.check_command("git push --force origin main")
        assert action == "block"
        assert "main" in msg.lower() or "dangerous" in msg.lower()

    def test_blocks_force_push_master(self, git_safety):
        """Should block force push to master."""
        action, msg, _ = git_safety.check_command("git push -f origin master")
        assert action == "block"

    def test_blocks_rm_git_directory(self, git_safety):
        """Should block removing .git directory."""
        action, msg, _ = git_safety.check_command("rm -rf .git")
        assert action == "block"
        assert "git" in msg.lower() or "history" in msg.lower()


class TestGitSafetyWarnings:
    """Test commands that should warn."""

    def test_warns_force_push_feature(self, git_safety):
        """Should warn on force push to non-main branch."""
        action, msg, suggestion = git_safety.check_command("git push --force origin feature-branch")
        assert action == "warn"
        assert suggestion is not None

    def test_warns_hard_reset(self, git_safety):
        """Should warn on hard reset."""
        action, msg, suggestion = git_safety.check_command("git reset --hard HEAD~1")
        assert action == "warn"
        assert "stash" in suggestion.lower() or "soft" in suggestion.lower()

    def test_warns_clean_fd(self, git_safety):
        """Should warn on git clean -fd."""
        action, msg, suggestion = git_safety.check_command("git clean -fd")
        assert action == "warn"
        assert "preview" in suggestion.lower() or "-n" in suggestion.lower()

    def test_warns_branch_force_delete(self, git_safety):
        """Should warn on force branch deletion."""
        action, msg, suggestion = git_safety.check_command("git branch -D feature")
        assert action == "warn"
        assert "-d" in suggestion.lower()

    def test_warns_rebase(self, git_safety):
        """Should warn on rebase."""
        action, msg, suggestion = git_safety.check_command("git rebase main")
        assert action == "warn"
        assert "backup" in suggestion.lower()


class TestGitSafetyAllowed:
    """Test commands that should be allowed."""

    def test_allows_regular_push(self, git_safety):
        """Should allow regular push."""
        action, _, _ = git_safety.check_command("git push origin feature-branch")
        assert action == "allow"

    def test_allows_soft_reset(self, git_safety):
        """Should allow soft reset."""
        action, _, _ = git_safety.check_command("git reset --soft HEAD~1")
        assert action == "allow"

    def test_allows_safe_branch_delete(self, git_safety):
        """Should allow safe branch deletion."""
        action, _, _ = git_safety.check_command("git branch -d feature")
        assert action == "allow"

    def test_allows_regular_commit(self, git_safety):
        """Should allow regular commit."""
        action, _, _ = git_safety.check_command("git commit -m 'test'")
        assert action == "allow"

    def test_allows_pull(self, git_safety):
        """Should allow git pull."""
        action, _, _ = git_safety.check_command("git pull origin main")
        assert action == "allow"

    def test_allows_non_git_commands(self, git_safety):
        """Should allow non-git commands."""
        action, _, _ = git_safety.check_command("npm install")
        assert action == "allow"

    def test_allows_rebase_abort(self, git_safety):
        """Should allow rebase abort."""
        action, _, _ = git_safety.check_command("git rebase --abort")
        assert action == "allow"

"""
Tests for skill-auto-activator hook.
"""

import pytest
import sys
import os

# Add hooks directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path fix
from importlib import import_module


@pytest.fixture
def skill_activator():
    """Import the skill activator module."""
    # Use importlib to handle the hyphenated filename
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "skill_activator",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "skill-auto-activator.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSkillSuggestion:
    """Test skill suggestion logic."""

    def test_suggests_debugging_for_bug(self, skill_activator):
        """Should suggest debugging skill for bug-related prompts."""
        result = skill_activator.suggest_skill("I have a bug in my code")
        assert result == "superpowers:systematic-debugging"

    def test_suggests_debugging_for_error(self, skill_activator):
        """Should suggest debugging skill for error-related prompts."""
        result = skill_activator.suggest_skill("Getting an error when running tests")
        assert result == "superpowers:systematic-debugging"

    def test_suggests_brainstorming_for_design(self, skill_activator):
        """Should suggest brainstorming for design prompts."""
        result = skill_activator.suggest_skill("Let's brainstorm some ideas")
        assert result == "superpowers:brainstorming"

    def test_suggests_tdd_for_implement(self, skill_activator):
        """Should suggest TDD for implementation prompts."""
        result = skill_activator.suggest_skill("Implement a new feature for users")
        assert result == "superpowers:test-driven-development"

    def test_suggests_tdd_for_test(self, skill_activator):
        """Should suggest TDD for test-related prompts."""
        result = skill_activator.suggest_skill("Write unit tests for this module")
        assert result == "superpowers:test-driven-development"

    def test_suggests_code_review(self, skill_activator):
        """Should suggest code review for review prompts."""
        result = skill_activator.suggest_skill("Please review my code changes")
        assert result == "superpowers:requesting-code-review"

    def test_suggests_verification_for_complete(self, skill_activator):
        """Should suggest verification for completion prompts."""
        result = skill_activator.suggest_skill("I'm done, ready to merge")
        assert result == "superpowers:verification-before-completion"

    def test_returns_none_for_generic(self, skill_activator):
        """Should return None for generic prompts."""
        result = skill_activator.suggest_skill("Hello, how are you?")
        assert result is None

    def test_case_insensitive(self, skill_activator):
        """Should match regardless of case."""
        assert skill_activator.suggest_skill("BUG") == "superpowers:systematic-debugging"
        assert skill_activator.suggest_skill("bug") == "superpowers:systematic-debugging"
        assert skill_activator.suggest_skill("Bug") == "superpowers:systematic-debugging"

    def test_handles_empty_string(self, skill_activator):
        """Should handle empty input."""
        result = skill_activator.suggest_skill("")
        assert result is None

    def test_handles_long_input(self, skill_activator):
        """Should handle very long input without hanging."""
        import time
        long_prompt = "test " * 50000  # 250k chars

        start = time.time()
        result = skill_activator.suggest_skill(long_prompt)
        elapsed = time.time() - start

        assert elapsed < 2.0  # Should complete quickly
        assert result is None  # No skill match expected


class TestSafeGetString:
    """Test safe_get_string helper."""

    def test_extracts_string(self, skill_activator):
        """Should extract string value."""
        data = {"key": "value"}
        result = skill_activator.safe_get_string(data, "key", "default")
        assert result == "value"

    def test_returns_default_for_missing(self, skill_activator):
        """Should return default for missing key."""
        data = {}
        result = skill_activator.safe_get_string(data, "key", "default")
        assert result == "default"

    def test_handles_none_value(self, skill_activator):
        """Should return default for None value."""
        data = {"key": None}
        result = skill_activator.safe_get_string(data, "key", "default")
        assert result == "default"

    def test_converts_non_string(self, skill_activator):
        """Should convert non-string to string."""
        data = {"key": 123}
        result = skill_activator.safe_get_string(data, "key", "default")
        assert result == "123"

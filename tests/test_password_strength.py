"""
Tests for password strength checker.
"""
import pytest
from src.utils.password_strength import check_password_strength


class TestPasswordStrength:
    """Test suite for password strength checking."""

    def test_empty_password(self):
        """Test that empty password returns none strength."""
        result = check_password_strength("")
        assert result["strength"] == "none"
        assert result["score"] == 0

    def test_very_short_password(self):
        """Test that very short passwords are weak."""
        result = check_password_strength("abc")
        assert result["strength"] == "weak"

    def test_short_password_weak(self):
        """Test short passwords without variety are weak."""
        result = check_password_strength("password")
        assert result["strength"] == "weak"

    def test_medium_password(self):
        """Test medium strength passwords."""
        result = check_password_strength("Password1")
        assert result["strength"] == "medium"

    def test_medium_password_longer(self):
        """Test medium strength with longer password."""
        result = check_password_strength("mypassword")
        # 9 chars + lowercase = score 2 = weak
        assert result["strength"] == "weak"

    def test_strong_password(self):
        """Test that strong passwords are recognized."""
        result = check_password_strength("MyP@ssw0rd!123")
        assert result["strength"] == "strong"

    def test_very_long_simple_password(self):
        """Test long passwords with mixed case and numbers."""
        result = check_password_strength("Password123456")
        # 14 chars + lowercase + uppercase + numbers = score 5 = strong
        assert result["strength"] == "strong"

    def test_all_character_types(self):
        """Test password with all character types."""
        result = check_password_strength("Aa1!Bb2@Cc3#Dd4$")
        assert result["strength"] == "strong"
        assert result["score"] >= 5

    def test_returns_dict_structure(self):
        """Test that function returns expected keys."""
        result = check_password_strength("test")
        assert "strength" in result
        assert "score" in result
        assert "color" in result
        assert "message" in result

    def test_score_range(self):
        """Test that score is within valid range."""
        result = check_password_strength("MyP@ssw0rd!123")
        assert 0 <= result["score"] <= 6

    def test_color_values(self):
        """Test that color is returned for different strengths."""
        weak = check_password_strength("abc")
        assert weak["color"] == "#F44336"  # Red

        medium = check_password_strength("Password1")
        assert medium["color"] == "#FFC107"  # Yellow

        strong = check_password_strength("MyP@ssw0rd!123")
        assert strong["color"] == "#4CAF50"  # Green

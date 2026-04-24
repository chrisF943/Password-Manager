"""
Tests for password generation utility.
"""
import pytest
import re
from src.utils.password_gen import generate_password, generate_and_copy_password


class TestPasswordGenerator:
    """Test suite for password generation."""

    def test_generate_default_length(self):
        """Test that default password has correct total length."""
        # Default: 6 letters + 3 numbers + 3 symbols = 12
        password = generate_password()
        assert len(password) == 12

    def test_generate_custom_counts(self):
        """Test password generation with custom character counts."""
        password = generate_password(num_letters=4, num_numbers=2, num_symbols=2)
        assert len(password) == 8

    def test_generate_contains_letters(self):
        """Test that password contains letters."""
        password = generate_password(num_letters=10, num_numbers=1, num_symbols=1)
        assert re.search(r'[a-zA-Z]', password) is not None

    def test_generate_contains_numbers(self):
        """Test that password contains numbers."""
        password = generate_password(num_letters=1, num_numbers=5, num_symbols=1)
        assert re.search(r'[0-9]', password) is not None

    def test_generate_contains_symbols(self):
        """Test that password contains special characters."""
        password = generate_password(num_letters=1, num_numbers=1, num_symbols=5)
        assert re.search(r'[!#$%&()*+]', password) is not None

    def test_generate_zero_letters(self):
        """Test password with zero letters."""
        password = generate_password(num_letters=0, num_numbers=5, num_symbols=2)
        assert len(password) == 7
        assert re.search(r'[0-9]', password) is not None

    def test_generate_zero_numbers(self):
        """Test password with zero numbers."""
        password = generate_password(num_letters=8, num_numbers=0, num_symbols=2)
        assert len(password) == 10
        assert re.search(r'[a-zA-Z]', password) is not None

    def test_generate_zero_symbols(self):
        """Test password with zero symbols."""
        password = generate_password(num_letters=8, num_numbers=2, num_symbols=0)
        assert len(password) == 10

    def test_generate_all_zeros(self):
        """Test password with all zero counts (edge case)."""
        password = generate_password(num_letters=0, num_numbers=0, num_symbols=0)
        # Returns empty string or might have edge case
        assert isinstance(password, str)

    def test_generate_returns_string(self):
        """Test that generate_password returns a string."""
        password = generate_password()
        assert isinstance(password, str)

    def test_generate_large_counts(self):
        """Test password with larger character counts."""
        password = generate_password(num_letters=20, num_numbers=10, num_symbols=10)
        assert len(password) == 40

    def test_generate_and_copy_returns_string(self):
        """Test that generate_and_copy_password returns a string."""
        password = generate_and_copy_password()
        assert isinstance(password, str)

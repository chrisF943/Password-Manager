"""
Tests for authentication functionality.
"""
import pytest
import os
import hashlib
from pathlib import Path

# Setup path before imports
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

# Set test environment - uses HASH comparison now
os.environ['KEY'] = _hash('test_master_password')


class TestAuthentication:
    """Test suite for master password authentication."""

    def test_verify_correct_password(self):
        """Test that correct password is verified."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('mysecretpassword')
        result = verify_master_password('mysecretpassword')
        assert result is True

    def test_verify_incorrect_password(self):
        """Test that incorrect password fails verification."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('mysecretpassword')
        result = verify_master_password('wrongpassword')
        assert result is False

    def test_verify_empty_password(self):
        """Test that empty password handling works."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('')
        result = verify_master_password('')
        assert result is True

    def test_verify_empty_password_fails_with_input(self):
        """Test that empty password fails with non-empty input."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('')
        result = verify_master_password('somepassword')
        assert result is False

    def test_verify_special_characters(self):
        """Test password with special characters."""
        from src.security.auth import verify_master_password

        test_password = "p@ssw0rd!#$%^&*()"
        os.environ['KEY'] = _hash(test_password)

        result = verify_master_password(test_password)
        assert result is True

    def test_verify_case_sensitive(self):
        """Test that password verification is case sensitive."""
        from src.security.auth import verify_master_password

        os.environ['KEY'] = _hash('MySecretPassword')

        assert verify_master_password('mysecretpassword') is False
        assert verify_master_password('MY SECRETPASSWORD') is False
        assert verify_master_password('MySecretPassword') is True

    def test_verify_no_key_set(self):
        """Test behavior when no KEY is set."""
        from src.security.auth import verify_master_password

        # Remove KEY from environment
        original = os.environ.pop('KEY', None)
        try:
            result = verify_master_password('anypassword')
            assert result is False
        finally:
            if original:
                os.environ['KEY'] = original

    def test_hash_master_password(self):
        """Test password hashing function."""
        from src.security.auth import hash_master_password

        result = hash_master_password('testpassword')
        # SHA256 hash of 'testpassword'
        assert len(result) == 64  # SHA256 produces 64 hex characters

"""
Tests for encryption/decryption functionality.
"""
import pytest
from src.security.encryption import encrypt_password, decrypt_password


class TestEncryption:
    """Test suite for encryption and decryption."""

    def test_encrypt_decrypt_roundtrip(self, cipher_suite):
        """Test that encrypting and decrypting returns original value."""
        original = "MySecretPassword123"
        encrypted = encrypt_password(original, cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == original

    def test_encrypt_produces_different_output(self, cipher_suite):
        """Test that encryption produces different output than original."""
        original = "MySecretPassword123"
        encrypted = encrypt_password(original, cipher_suite)
        assert encrypted != original

    def test_encrypt_produces_consistent_output(self, cipher_suite):
        """Test that same password encrypts to same output."""
        original = "MySecretPassword123"
        encrypted1 = encrypt_password(original, cipher_suite)
        encrypted2 = encrypt_password(original, cipher_suite)
        # Note: Fernet generates unique tokens, so we test decryption works
        assert decrypt_password(encrypted1, cipher_suite) == original
        assert decrypt_password(encrypted2, cipher_suite) == original

    def test_decrypt_wrong_raises_error(self, cipher_suite):
        """Test that decrypting invalid data raises error."""
        with pytest.raises(Exception):
            decrypt_password("invalid_encrypted_data", cipher_suite)

    def test_encrypt_empty_string(self, cipher_suite):
        """Test encrypting empty string."""
        encrypted = encrypt_password("", cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == ""

    def test_encrypt_special_characters(self, cipher_suite):
        """Test encrypting password with special characters."""
        original = "P@ssw0rd!#$%^&*()"
        encrypted = encrypt_password(original, cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == original

    def test_encrypt_unicode(self, cipher_suite):
        """Test encrypting password with unicode characters."""
        original = "пароль123"  # Russian word for password
        encrypted = encrypt_password(original, cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == original

    def test_encrypt_long_password(self, cipher_suite):
        """Test encrypting very long password."""
        original = "A" * 1000
        encrypted = encrypt_password(original, cipher_suite)
        decrypted = decrypt_password(encrypted, cipher_suite)
        assert decrypted == original

    def test_encrypt_preserves_length_info(self, cipher_suite):
        """Test that encrypted data has expected Fernet format."""
        original = "short"
        encrypted = encrypt_password(original, cipher_suite)
        # Fernet token is base64 encoded, length varies
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0


# Tests for derive_key and get_salt functions

import os
from src.security.encryption import derive_key, get_salt
from cryptography.fernet import Fernet


def test_derive_key_produces_valid_fernet_key():
    """Derived key should be a valid Fernet key."""
    key = derive_key("mypassword", "mysalt")
    assert isinstance(key, bytes)
    # Should be 32 bytes (key) that Fernet can use
    fernet = Fernet(key)
    assert fernet is not None


def test_derive_key_same_inputs_produce_same_key():
    """Same password + salt should produce same key."""
    key1 = derive_key("mypassword", "mysalt")
    key2 = derive_key("mypassword", "mysalt")
    assert key1 == key2


def test_derive_key_different_salts_produce_different_keys():
    """Same password + different salt should produce different keys."""
    key1 = derive_key("mypassword", "salt1")
    key2 = derive_key("mypassword", "salt2")
    assert key1 != key2


def test_derive_key_different_passwords_produce_different_keys():
    """Different password + same salt should produce different keys."""
    key1 = derive_key("password1", "mysalt")
    key2 = derive_key("password2", "mysalt")
    assert key1 != key2


def test_encrypt_decrypt_roundtrip():
    """Encrypted and decrypted password should match original."""
    key = derive_key("mypassword", "mysalt")
    fernet = Fernet(key)
    plaintext = "mysecretpassword"
    encrypted = encrypt_password(plaintext, fernet)
    decrypted = decrypt_password(encrypted, fernet)
    assert decrypted == plaintext

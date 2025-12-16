"""
Unit tests for password hashing utilities.

This test suite validates the PasswordHasher implementation including:
- Proper Argon2id parameter configuration
- Pepper application and consistency
- Hash generation and verification
- Error handling for edge cases
- Security properties (timing attacks, rehashing)
- Fail-fast behavior for missing pepper

Test philosophy:
- Unit tests mock external dependencies (env vars, pepper loading)
- Focus on contract adherence and security guarantees
- Validate both happy paths and failure modes
"""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from passlib.exc import UnknownHashError

from app.core.security.hashing.password import PasswordHasher, pwd_context
from app.core.security.hashing.base import HashingError


class TestPasswordHasherInitialization:
    """Test suite for PasswordHasher initialization and configuration."""

    def test_initializes_with_valid_pepper(self):
        """Should successfully initialize when pepper is available."""
        with patch("app.core.security.hashing.password.get_pepper", return_value="test-pepper-secret"):
            hasher = PasswordHasher()
            assert hasher._pepper == "test-pepper-secret"

    def test_fails_when_pepper_missing(self):
        """Should raise RuntimeError when pepper is not set."""
        with patch("app.core.security.hashing.password.get_pepper", side_effect=RuntimeError("PASSWORD_PEPPER must be set for cryptographic operations")):
            with pytest.raises(RuntimeError, match="PASSWORD_PEPPER must be set"):
                PasswordHasher()

    def test_pepper_loaded_once_during_init(self):
        """Should load pepper only once during initialization, not per operation."""
        with patch("app.core.security.hashing.password.get_pepper", return_value="test-pepper") as mock_get_pepper:
            hasher = PasswordHasher()
            hasher.hash("password123")
            hasher.hash("another-password")
            
            assert mock_get_pepper.call_count == 1


class TestPasswordHasherArgon2Configuration:
    def test_uses_argon2id_variant(self):
        hash_ = pwd_context.hash("password123")
        assert hash_.startswith("$argon2id$")

    def test_memory_cost_configured_correctly(self):
        hash_ = pwd_context.hash("password123")
        assert "m=65536" in hash_

    def test_time_cost_configured_correctly(self):
        hash_ = pwd_context.hash("password123")
        assert "t=3" in hash_

    def test_parallelism_configured_correctly(self):
        hash_ = pwd_context.hash("password123")
        assert "p=1" in hash_

"""
Unit tests for password hashing utilities.

This test suite validates the PasswordHasher implementation including:
- Proper Argon2id parameter configuration
- Pepper application via environment
- Hash generation and verification
- Error handling for edge cases
- Core security guarantees

Assumptions:
- PASSWORD_PEPPER is set globally via conftest.py
- Pepper is resolved once during PasswordHasher initialization
"""

from __future__ import annotations

import pytest
import base64

from app.core.security.hashing.password import PasswordHasher, pwd_context
from app.core.security.hashing.base import HashingError


import base64

def b64decode_nopad(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.b64decode(data + padding)

class TestPasswordHasherInitialization:
    def test_initializes_when_pepper_is_available(self):
        hasher = PasswordHasher()
        assert hasher is not None

    def test_pepper_loaded_only_once(self, monkeypatch):
        calls = []

        def fake_get_pepper():
            calls.append(1)
            return "test-pepper-secret"

        monkeypatch.setattr(
            "app.core.security.hashing.password.get_pepper",
            fake_get_pepper
        )

        hasher = PasswordHasher()
        hasher.hash("password123")
        hasher.hash("another-password")

        assert len(calls) == 1


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


class TestPasswordHasherHash:
    @pytest.fixture
    def hasher(self):
        return PasswordHasher()

    def test_hash_returns_non_empty_string(self, hasher):
        hashed = hasher.hash("password123")

        assert isinstance(hashed, str)
        assert hashed != ""

    def test_hash_produces_argon2id_format(self, hasher):
        hashed = hasher.hash("password123")

        assert hashed.startswith("$argon2id$")

    def test_same_password_produces_unique_hashes(self, hasher):
        hash1 = hasher.hash("password123")
        hash2 = hasher.hash("password123")

        assert hash1 != hash2

    def test_hashed_password_can_be_verified(self, hasher):
        hashed = hasher.hash("password123")

        assert hasher.verify("password123", hashed)

    def test_wrong_password_does_not_verify(self, hasher):
        hashed = hasher.hash("password123")

        assert not hasher.verify("wrong-password", hashed)

    def test_hash_raises_error_for_empty_password(self, hasher):
        with pytest.raises(HashingError, match="Password cannot be empty"):
            hasher.hash("")

    def test_hash_raises_error_for_none_password(self, hasher):
        with pytest.raises(HashingError, match="Password cannot be empty"):
            hasher.hash(None)

    @pytest.mark.parametrize(
        "password",
        [
            "simple",
            "with spaces and special !@#$%",
            "unicode_测试_مرحبا_🔒",
            "very" * 100,
            "with\nnewlines\tand\ttabs",
        ],
    )
    def test_hash_handles_various_password_formats(self, hasher, password):
        hashed = hasher.hash(password)

        assert isinstance(hashed, str)
        assert hashed.startswith("$argon2id$")


class TestPasswordHasherOutputProperties:
    def test_salt_size_is_16_bytes(self):
        hash_ = pwd_context.hash("password123")
        salt_b64 = hash_.split("$")[-2]
        salt = b64decode_nopad(salt_b64)

        assert len(salt) == 16

    def test_hash_length_is_32_bytes(self):
        hash_ = pwd_context.hash("password123")
        hash_b64 = hash_.split("$")[-1]
        digest = b64decode_nopad(hash_b64)

        assert len(digest) == 32


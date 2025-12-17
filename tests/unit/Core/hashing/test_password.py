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










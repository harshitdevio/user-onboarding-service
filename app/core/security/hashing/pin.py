from __future__ import annotations

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from .base import get_pepper, apply_pepper, HashingError

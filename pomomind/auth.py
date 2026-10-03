"""Authentication.

DEMO ONLY: accounts are hard-coded and passwords are unsalted SHA-256.
Replace `_ACCOUNTS` / `authenticate` with a real identity provider before
any real deployment. Demo credentials are listed in the README.
"""
import hashlib
import hmac
from typing import Optional

from pomomind.config import ROLE_PROFESSOR, ROLE_STUDENT
from pomomind.models import User


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# username -> (password hash, user)
_ACCOUNTS = {
    "student": (
        "703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b",
        User("student", ROLE_STUDENT),
    ),
    "prof_bio": (
        "d6ab4145fcbe6946a27685119639b7f2271a786b4dd0e3ead33433e1c336827f",
        User("prof_bio", ROLE_PROFESSOR, "Biologie"),
    ),
    "prof_cyber": (
        "fc6d919ca14406c1be2c90867a8a334951b5f1e7c3f8b2650a604990379f5a54",
        User("prof_cyber", ROLE_PROFESSOR, "Cybersecurity"),
    ),
}


def authenticate(username: str, password: str, role: str) -> Optional[User]:
    """Return the User if credentials and chosen role all match, else None."""
    record = _ACCOUNTS.get(username)
    if record is None:
        return None
    password_hash, user = record
    if hmac.compare_digest(hash_password(password), password_hash) and user.role == role:
        return user
    return None

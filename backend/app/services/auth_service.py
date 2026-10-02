"""
Staff authentication: password hashing with PBKDF2-HMAC-SHA256 (Python's
built-in hashlib -- no extra dependency needed) and JWT session tokens.

Registration is open (no invite code) so any new staff member can create
their own account with a name, role, and department -- swap `STAFF_USERS`
for a real `staff` table (same hashing) when moving off the in-memory store.
"""
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
TOKEN_TTL = timedelta(hours=8)

STAFF_ROLES = ["receptionist", "nurse", "doctor", "admin"]


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()


def _make_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    return salt.hex() + ":" + _hash_password(password, salt)


def _verify_password(password: str, stored_hash: str) -> bool:
    salt_hex, hash_hex = stored_hash.split(":")
    salt = bytes.fromhex(salt_hex)
    return secrets.compare_digest(_hash_password(password, salt), hash_hex)


def _seed_account(username: str, password: str, full_name: str, role: str) -> dict:
    return {"password_hash": _make_hash(password), "full_name": full_name, "role": role}


# Demo staff account: username "admin", password "admin123" -- hashed, not
# plaintext. Real accounts are added via register_staff() below.
STAFF_USERS: dict[str, dict] = {
    "admin": _seed_account("admin", "admin123", "Default Admin", "admin"),
}


def register_staff(username: str, password: str, full_name: str, role: str) -> str | None:
    """Returns an error message on failure, or None on success. Open
    registration -- no invite code -- since anyone with the app link is
    assumed to be a legitimate staff member for this project's scope."""
    username = username.strip().lower()
    if username in STAFF_USERS:
        return "That username is already taken."
    if len(username) < 3:
        return "Username must be at least 3 characters."
    if len(password) < 6:
        return "Password must be at least 6 characters."
    if role not in STAFF_ROLES:
        return "Please choose a valid role."
    STAFF_USERS[username] = _seed_account(username, password, full_name.strip() or username, role)
    return None


def authenticate(username: str, password: str) -> bool:
    user = STAFF_USERS.get(username.strip().lower())
    if not user:
        return False
    return _verify_password(password, user["password_hash"])


def get_profile(username: str) -> dict | None:
    user = STAFF_USERS.get(username)
    if not user:
        return None
    return {"username": username, "full_name": user["full_name"], "role": user["role"]}


def create_token(username: str) -> str:
    payload = {
        "sub": username.strip().lower(),
        "exp": datetime.now(timezone.utc) + TOKEN_TTL,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> str | None:
    """Returns the username if the token is valid, else None."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None

"""API-key authentication and role checks."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets

from .errors import AuthenticationError, AuthorizationError, ConflictError, ValidationError
from .storage import Database, Principal, ROLE_LEVEL


class AuthService:
    PREFIX_BYTES = 8
    ROUNDS = 210_000

    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def _encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @classmethod
    def _hash(cls, token: str, salt: bytes) -> str:
        digest = hashlib.pbkdf2_hmac("sha256", token.encode("utf-8"), salt, cls.ROUNDS)
        return f"pbkdf2-sha256${cls.ROUNDS}${cls._encode(salt)}${cls._encode(digest)}"

    @classmethod
    def _verify_hash(cls, token: str, encoded: str) -> bool:
        try:
            algorithm, rounds, salt, expected = encoded.split("$", 3)
            if algorithm != "pbkdf2-sha256":
                return False
            actual = hashlib.pbkdf2_hmac("sha256", token.encode("utf-8"), base64.urlsafe_b64decode(salt + "=="), int(rounds))
            return hmac.compare_digest(cls._encode(actual), expected)
        except (ValueError, TypeError):
            return False

    def issue_key(self, tenant_id: str, user_id: str) -> str:
        token = "eai_" + self._encode(secrets.token_bytes(32))
        prefix = token[: 4 + self.PREFIX_BYTES * 2]
        key_id = self.db.insert_api_key(tenant_id, user_id, prefix, self._hash(token, os.urandom(16)))
        return f"{token}.{key_id}"

    def rotate_current(self, principal: Principal) -> str:
        """Issue a replacement key before revoking the current key."""
        replacement = self.issue_key(principal.tenant_id, principal.user_id)
        self.db.revoke_api_key(principal.tenant_id, principal.api_key_id)
        return replacement

    def issue_for_user(self, principal: Principal, user_id: str) -> str:
        self.require(principal, "admin")
        self.db.require_user(principal.tenant_id, user_id)
        return self.issue_key(principal.tenant_id, user_id)

    def revoke(self, principal: Principal, key_id: str) -> None:
        self.require(principal, "admin")
        self.db.revoke_api_key(principal.tenant_id, key_id)

    def create_user(self, principal: Principal, email: str, role: str) -> dict[str, object]:
        self.require(principal, "admin")
        self._require_assignable_role(principal, role)
        user_id = self.db.create_user(principal.tenant_id, email, role)
        return self.db.get_user(principal.tenant_id, user_id)

    def list_users(self, principal: Principal) -> list[dict[str, object]]:
        self.require(principal, "admin")
        return self.db.list_users(principal.tenant_id)

    def update_user_role(self, principal: Principal, user_id: str, role: str) -> dict[str, object]:
        self.require(principal, "admin")
        if principal.user_id == user_id:
            raise ConflictError("use a different owner to change your own role")
        target = self.db.get_user(principal.tenant_id, user_id)
        if target["role"] == "owner" and principal.role != "owner":
            raise AuthorizationError("only an owner can change another owner's role")
        self._require_assignable_role(principal, role)
        return self.db.update_user_role(principal.tenant_id, user_id, role)

    @staticmethod
    def _require_assignable_role(principal: Principal, role: str) -> None:
        if role not in ROLE_LEVEL:
            raise ValidationError("role must be viewer, operator, admin, or owner")
        if ROLE_LEVEL[role] > ROLE_LEVEL.get(principal.role, 0):
            raise AuthorizationError("cannot assign a role higher than your own")

    def authenticate(self, presented: str | None) -> Principal:
        if not presented or not presented.startswith("eai_") or "." not in presented:
            raise AuthenticationError("use an eai_ API key")
        token, key_id = presented.rsplit(".", 1)
        principal = self.db.user_for_api_key(key_id)
        if principal is None:
            raise AuthenticationError("invalid or revoked API key")
        with self.db.connect() as conn:
            row = conn.execute("SELECT key_prefix,key_hash FROM api_keys WHERE id=? AND revoked_at IS NULL", (key_id,)).fetchone()
        if row is None or row["key_prefix"] != token[: 4 + self.PREFIX_BYTES * 2] or not self._verify_hash(token, row["key_hash"]):
            raise AuthenticationError("invalid or revoked API key")
        return principal

    @staticmethod
    def require(principal: Principal, role: str) -> None:
        if role not in ROLE_LEVEL:
            raise ValidationError("unknown required role")
        if ROLE_LEVEL.get(principal.role, 0) < ROLE_LEVEL[role]:
            raise AuthorizationError(f"role {role} or higher is required")

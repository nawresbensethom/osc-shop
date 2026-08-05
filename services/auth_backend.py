from __future__ import annotations

from dataclasses import dataclass

from flask import current_app, request

from models import User


@dataclass(slots=True)
class AuthIdentity:
    username: str
    email: str = ""
    full_name: str = ""
    role: str = "user"


class AuthBackend:
    def authenticate(self, username: str, password: str) -> User | None:  # pragma: no cover - interface
        raise NotImplementedError

    def get_proxy_identity(self) -> AuthIdentity | None:  # pragma: no cover - interface
        raise NotImplementedError


class LocalAuthBackend(AuthBackend):
    def authenticate(self, username: str, password: str) -> User | None:
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password) and user.is_active_account:
            return user
        return None

    def get_proxy_identity(self) -> AuthIdentity | None:
        return None


class HeaderAuthBackend(AuthBackend):
    def authenticate(self, username: str, password: str) -> User | None:
        return None

    def get_proxy_identity(self) -> AuthIdentity | None:
        proxy_user = request.headers.get("X-Forwarded-User")
        if not proxy_user:
            return None
        return AuthIdentity(
            username=proxy_user,
            email=request.headers.get("X-Forwarded-Email", ""),
            full_name=request.headers.get("X-Forwarded-Name", proxy_user),
            role=request.headers.get("X-Forwarded-Role", "user"),
        )


def get_auth_backend() -> AuthBackend:
    mode = current_app.config.get("AUTH_MODE", "local").lower()
    return HeaderAuthBackend() if mode == "proxy" else LocalAuthBackend()

from __future__ import annotations

from models import User


def create_user(username: str, email: str, password: str, full_name: str, role: str = "user") -> User:
    user = User(username=username, email=email, full_name=full_name, role=role)
    user.set_password(password)
    return user


def authenticate_local(username: str, password: str) -> User | None:
    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if user and user.check_password(password) and user.is_active_account:
        return user
    return None

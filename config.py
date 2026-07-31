from __future__ import annotations

import os


def _bool(value: str | bool | None, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-now")
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///osc_shop.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    WTF_CSRF_TIME_LIMIT: int | None = None
    APP_NAME: str = os.getenv("APP_NAME", "OSC Shop")
    AUTH_MODE: str = os.getenv("AUTH_MODE", "local")
    PREFERRED_URL_SCHEME: str = os.getenv("PREFERRED_URL_SCHEME", "http")
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SECURE: bool = _bool(os.getenv("SESSION_COOKIE_SECURE"), False)
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    REMEMBER_COOKIE_HTTPONLY: bool = True
    REMEMBER_COOKIE_SECURE: bool = _bool(os.getenv("REMEMBER_COOKIE_SECURE"), False)
    REMEMBER_COOKIE_SAMESITE: str = os.getenv("REMEMBER_COOKIE_SAMESITE", "Lax")
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True


class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    TESTING: bool = False


class TestingConfig(BaseConfig):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False


def get_config(name: str | None = None) -> type[BaseConfig]:
    lookup = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    return lookup.get((name or os.getenv("FLASK_ENV", "development")).lower(), DevelopmentConfig)

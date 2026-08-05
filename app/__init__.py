from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, session, url_for
from flask_login import current_user, logout_user

from config import get_config
from extensions import csrf, db, login_manager
from models import User
from routes import register_blueprints
from routes.oidc import oidc_bp
from services.seed_service import seed_demo_data
from utils.logging import RequestLogFormatter
from utils.security import add_security_headers

DEMO_FLAGS = [
    "ENABLE_SQLI",
    "ENABLE_XSS",
    "ENABLE_IDOR",
    "ENABLE_UPLOAD",
    "ENABLE_BRUTE_FORCE",
    "ENABLE_DEBUG_ERRORS",
    "ENABLE_ENUMERATION",
    "ENABLE_RATE_LIMITING",
    "ENABLE_CSRF",
    "ENABLE_INSECURE_COOKIES",
    "ENABLE_WEAK_HEADERS",
]


def _configure_logging(app: Flask) -> None:
    logs_dir = Path(app.instance_path) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(logs_dir / "osc_shop.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(RequestLogFormatter())
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True, template_folder="../templates", static_folder="../static")
    app.config.from_object(get_config(config_name))
    app.config.from_prefixed_env()

    try:
        import demo_config as demo_module

        for flag_name in DEMO_FLAGS:
            app.config[flag_name] = bool(getattr(demo_module, flag_name, False))
    except Exception:
        for flag_name in DEMO_FLAGS:
            app.config.setdefault(flag_name, False)

    if app.config.get("ENABLE_INSECURE_COOKIES"):
        app.config["SESSION_COOKIE_HTTPONLY"] = False
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["REMEMBER_COOKIE_HTTPONLY"] = False
        app.config["REMEMBER_COOKIE_SECURE"] = False
        app.config["REMEMBER_COOKIE_SAMESITE"] = "None"

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    _configure_logging(app)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" if not app.config.get("OIDC_ENABLED", False) else "oidc.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        if not user_id:
            return None
        return db.session.get(User, int(user_id))

    register_blueprints(app)
    add_security_headers(app)

    @app.before_request
    def _request_context() -> None:
        g.client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
        g.user_agent = request.headers.get("User-Agent", "unknown")

    @app.before_request
    def _enforce_oidc_access() -> object | None:
        if not app.config.get("OIDC_ENABLED", False):
            return None

        if request.path.startswith("/static") or request.path.startswith("/favicon"):
            return None

        allowed_paths = {"/login", "/callback", "/logout", "/auth/login", "/auth/register"}
        if request.path in allowed_paths:
            return None

        if current_user.is_authenticated and session.get("oidc_claims"):
            return None

        if current_user.is_authenticated:
            logout_user()
            session.clear()
            return redirect(url_for("oidc.login", next=request.url))

        session["next"] = request.url
        return redirect(url_for("oidc.login", next=request.url))

    @app.context_processor
    def _inject_globals() -> dict[str, object]:
        return {"app_name": app.config.get("APP_NAME", "OSC Shop")}

    @app.cli.command("init-db")
    def init_db_command() -> None:
        with app.app_context():
            db.create_all()
            seed_demo_data(app)
        print("Database initialized.")

    @app.errorhandler(404)
    def not_found(_error: Exception):  # noqa: ANN401
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error: Exception):  # noqa: ANN401
        app.logger.exception("Server error", extra={"client_ip": getattr(g, "client_ip", "unknown"), "user_agent": getattr(g, "user_agent", "unknown")})
        return render_template("errors/500.html"), 500

    @app.errorhandler(429)
    def too_many_requests(_error: Exception):  # noqa: ANN401
        return render_template("errors/429.html"), 429

    with app.app_context():
        db.create_all()
        seed_demo_data(app)

    return app

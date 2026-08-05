from __future__ import annotations

from flask import current_app, g


def log_action(message: str) -> None:
    current_app.logger.info(message, extra={"client_ip": getattr(g, "client_ip", "unknown"), "user_agent": getattr(g, "user_agent", "unknown")})

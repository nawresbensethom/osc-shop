from __future__ import annotations

from flask import Flask


def add_security_headers(app: Flask) -> None:
    @app.after_request
    def _apply_headers(response):  # noqa: ANN001
        if app.config.get("ENABLE_WEAK_HEADERS", False):
            response.headers["X-Powered-By"] = "OSC Shop Demo"
        else:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; img-src 'self' https://via.placeholder.com data:; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "script-src 'self' https://cdn.jsdelivr.net"
            )
        return response

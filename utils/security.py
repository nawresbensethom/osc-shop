from __future__ import annotations

from flask import Flask

from demo_config import ENABLE_WEAK_HEADERS


def add_security_headers(app: Flask) -> None:
    @app.after_request
    def _apply_headers(response):  # noqa: ANN001
        if ENABLE_WEAK_HEADERS:
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

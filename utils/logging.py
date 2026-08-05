from __future__ import annotations

import logging
import json
from datetime import datetime, timezone

from flask import has_request_context, g


class RequestLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "client_ip": getattr(record, "client_ip", None)
            or (getattr(g, "client_ip", None) if has_request_context() else None)
            or "unknown",
            "user_agent": getattr(record, "user_agent", None)
            or (getattr(g, "user_agent", None) if has_request_context() else None)
            or "unknown",
        }
        return json.dumps(payload, ensure_ascii=False)


def log_event(logger: logging.Logger, message: str, *, client_ip: str | None = None, user_agent: str | None = None, level: int = logging.INFO) -> None:
    if has_request_context():
        client_ip = client_ip or getattr(g, "client_ip", "unknown")
        user_agent = user_agent or getattr(g, "user_agent", "unknown")
    logger.log(level, message, extra={"client_ip": client_ip or "unknown", "user_agent": user_agent or "unknown"})

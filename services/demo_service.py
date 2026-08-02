from __future__ import annotations

from flask import current_app


def demo_flag(name: str) -> bool:
    try:
        return bool(current_app.config.get(name, False))
    except RuntimeError:
        from importlib import import_module

        module = import_module("demo_config")
        return bool(getattr(module, name, False))

from __future__ import annotations

from importlib import import_module


def demo_flag(name: str) -> bool:
    module = import_module("demo_config")
    return bool(getattr(module, name, False))

from __future__ import annotations

from typing import Any


def normalize_groups(groups: Any) -> list[str]:
    if not groups:
        return []
    if isinstance(groups, str):
        return [groups]
    if isinstance(groups, (list, tuple, set)):
        return [str(item) for item in groups if str(item)]
    return []


def has_required_group(user_groups: Any, required_groups: set[str] | None = None) -> bool:
    required_groups = required_groups or {"app-users"}
    return any(group in required_groups for group in normalize_groups(user_groups))

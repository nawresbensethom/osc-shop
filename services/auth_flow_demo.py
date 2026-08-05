from __future__ import annotations

from typing import Any

import requests


def build_flow_status(app_config: dict[str, Any], session_data: dict[str, Any], *, authenticated: bool = False) -> dict[str, Any]:
    oidc_enabled = bool(app_config.get("OIDC_ENABLED", False))
    provider_name = str(app_config.get("OIDC_PROVIDER_NAME", "Keycloak")).strip() or "Keycloak"
    metadata_url = app_config.get("OIDC_METADATA_URL", app_config.get("KEYCLOAK_METADATA_URL", ""))
    required_groups = {
        group.strip()
        for group in str(app_config.get("OIDC_REQUIRED_GROUPS", app_config.get("KEYCLOAK_REQUIRED_GROUPS", ""))).split(",")
        if group.strip()
    }

    metadata_ok = False
    metadata_message = "not configured"
    if metadata_url:
        try:
            response = requests.get(metadata_url, timeout=5)
            metadata_ok = response.ok
            metadata_message = f"HTTP {response.status_code}" if not response.ok else "reachable"
        except Exception as exc:  # pragma: no cover - exercised at runtime
            metadata_message = str(exc)

    claims = session_data.get("oidc_claims") or {}
    groups = session_data.get("oidc_groups") or []
    has_required_group = bool(required_groups and any(group in required_groups for group in groups)) if required_groups else True

    steps = [
        {
            "name": "OIDC enabled",
            "ok": oidc_enabled,
            "detail": f"OIDC is enabled in the app configuration for {provider_name}." if oidc_enabled else "OIDC is disabled; enable it to test the login flow.",
        },
        {
            "name": f"{provider_name} metadata reachable",
            "ok": metadata_ok,
            "detail": metadata_message,
        },
        {
            "name": "User authenticated",
            "ok": authenticated,
            "detail": "The app has a signed-in user session." if authenticated else "No authenticated user session yet.",
        },
        {
            "name": "OIDC claims received",
            "ok": bool(claims),
            "detail": f"{provider_name} returned user claims to the app." if claims else "No claims were captured in the current session.",
        },
        {
            "name": "Required group present",
            "ok": has_required_group,
            "detail": f"Required groups: {', '.join(sorted(required_groups)) or 'none'}" if required_groups else "No required groups configured.",
        },
    ]

    if oidc_enabled and metadata_ok and authenticated and claims and has_required_group:
        status = "working"
        summary = f"The {provider_name} login flow is working and the app received a valid session."
    elif oidc_enabled and metadata_ok and not authenticated:
        status = "awaiting-login"
        summary = f"The {provider_name} server is reachable. Start the login flow to prove the OIDC hand-off."
    elif oidc_enabled and not metadata_ok:
        status = "metadata-unreachable"
        summary = f"The app cannot reach the {provider_name} discovery endpoint yet."
    else:
        status = "not-ready"
        summary = "The login workflow is not ready yet."

    return {
        "status": status,
        "summary": summary,
        "steps": steps,
        "metadata_url": metadata_url,
        "required_groups": sorted(required_groups),
        "groups": sorted(groups),
    }

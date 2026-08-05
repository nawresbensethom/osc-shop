from __future__ import annotations

import os
from typing import Any

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, abort, current_app, flash, redirect, request, session, url_for
from flask_login import current_user, login_user, logout_user

from extensions import db
from models import User
from services.oidc_service import has_required_group, normalize_groups

oidc_bp = Blueprint("oidc", __name__)


def _provider_label() -> str:
    return str(current_app.config.get("OIDC_PROVIDER_NAME", "Keycloak")).strip() or "Keycloak"


def _get_oauth() -> OAuth:
    if not hasattr(current_app, "oidc_oauth"):
        oauth = OAuth(current_app)
        oauth.register(
            name="keycloak",
            server_metadata_url=current_app.config.get("OIDC_METADATA_URL"),
            client_id=current_app.config.get("OIDC_CLIENT_ID"),
            client_secret=current_app.config.get("OIDC_CLIENT_SECRET", ""),
            client_kwargs={"scope": "openid profile email"},
        )
        current_app.oidc_oauth = oauth
    return current_app.oidc_oauth


def _get_required_groups() -> set[str]:
    raw_groups = current_app.config.get("OIDC_REQUIRED_GROUPS", "")
    if isinstance(raw_groups, str):
        return {group.strip() for group in raw_groups.split(",") if group.strip()}
    return {str(group).strip() for group in raw_groups or [] if str(group).strip()}


def _build_redirect_uri(request_obj: Any) -> str:
    configured = current_app.config.get("OIDC_REDIRECT_URI")
    if configured:
        return str(configured)
    return request_obj.host_url.rstrip("/") + "/callback"


def _get_user_groups(claims: dict[str, Any]) -> list[str]:
    if not claims:
        return []
    groups = claims.get("groups")
    if groups:
        return normalize_groups(groups)
    realm_access = claims.get("realm_access") or {}
    roles = realm_access.get("roles") or []
    if roles:
        return normalize_groups(roles)
    return []


def _ensure_local_user(claims: dict[str, Any]) -> User:
    username = claims.get("preferred_username") or claims.get("sub") or "oidc-user"
    email = claims.get("email") or f"{username}@local"
    full_name = claims.get("name") or claims.get("preferred_username") or username

    user = User.query.filter((User.username == username) | (User.email == email)).first()
    if user is None:
        user = User(username=username, email=email, full_name=full_name, role="user", bio="")
        user.set_password(os.urandom(16).hex())
        db.session.add(user)

    user.username = username
    user.email = email
    user.full_name = full_name
    user.is_active_account = True
    db.session.commit()
    return user


@oidc_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for("main.index"))

    oauth = _get_oauth()
    nonce = os.urandom(16).hex()
    session["oidc_nonce"] = nonce
    redirect_uri = _build_redirect_uri(request)
    current_app.logger.info("OIDC login redirect_uri=%s", redirect_uri)

    try:
        return oauth.keycloak.authorize_redirect(redirect_uri, nonce=nonce, prompt="login")
    except Exception as exc:
        current_app.logger.exception("OIDC login failed: %s", exc)
        flash(f"La connexion {_provider_label()} n'a pas pu être lancée. Vérifiez l'URL du serveur, le client OIDC et l'URI de redirection.", "danger")
        return redirect(url_for("main.index"))


@oidc_bp.route("/callback")
def callback():
    oauth = _get_oauth()
    try:
        token = oauth.keycloak.authorize_access_token()
    except Exception as exc:
        current_app.logger.exception("OIDC callback failed: %s", exc)
        flash(f"La réception du jeton {_provider_label()} a échoué. Vérifiez l'URL de redirection et le client OIDC.", "danger")
        return redirect(url_for("main.index"))

    claims: dict[str, Any] = {}
    try:
        claims = oauth.keycloak.userinfo(token=token.get("access_token"))
    except Exception:
        claims = {}

    if not claims:
        try:
            claims = oauth.keycloak.parse_id_token(token, nonce=session.get("oidc_nonce"))
        except Exception:
            claims = {}

    if not claims:
        current_app.logger.error("OIDC callback produced no user claims")
        abort(401)

    groups = _get_user_groups(claims)
    required_groups = _get_required_groups()
    if required_groups and not has_required_group(groups, required_groups):
        session.clear()
        flash(f"Authentification réussie, mais votre compte ne possède pas les groupes requis dans {_provider_label()}.", "warning")
        return redirect(url_for("main.index"))

    user = _ensure_local_user(claims)
    login_user(user, remember=True)
    session["oidc_groups"] = groups
    session["oidc_claims"] = claims

    next_url = session.pop("next", None) or request.args.get("next") or url_for("main.index")
    return redirect(next_url)


@oidc_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.index"))

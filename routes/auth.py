from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from forms.auth import LoginForm, ProfileForm, RegisterForm
from models import User
from services.auth_backend import get_auth_backend
from services.demo_service import demo_flag
from utils.logging import log_event
from utils.rate_limit import check_rate_limit

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            if demo_flag("ENABLE_ENUMERATION"):
                if existing_user.username == form.username.data:
                    form.username.errors.append("Ce nom d'utilisateur est déjà utilisé.")
                if existing_user.email == form.email.data:
                    form.email.errors.append("Cet email est déjà utilisé.")
            else:
                flash("Impossible de créer le compte avec ces informations.", "danger")
            return render_template("auth/register.html", form=form)
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            bio="",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_event(current_app.logger, "registration_success")
        flash("Compte créé avec succès.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        client_ip = getattr(request, "remote_addr", "unknown") or "unknown"
        if not demo_flag("ENABLE_BRUTE_FORCE"):
            limit_result = check_rate_limit(
                f"login:{client_ip}",
                limit=5 if not demo_flag("ENABLE_RATE_LIMITING") else 3,
                window_seconds=60,
            )
            if not limit_result.allowed:
                log_event(current_app.logger, "login_rate_limited")
                flash("Trop de tentatives. Réessayez plus tard.", "warning")
                return render_template("auth/login.html", form=form), 429
        backend = get_auth_backend()
        user = backend.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()
            log_event(current_app.logger, "login_success")
            next_url = request.args.get("next") or url_for("main.index")
            return redirect(next_url)
        log_event(current_app.logger, "login_failed")
        if demo_flag("ENABLE_ENUMERATION"):
            known_user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
            if known_user:
                flash("Le mot de passe est incorrect.", "danger")
            else:
                flash("Ce compte n'existe pas.", "danger")
        else:
            flash("Identifiants invalides.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_event(current_app.logger, "logout")
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        existing_email = User.query.filter(User.email == form.email.data, User.id != current_user.id).first()
        if existing_email:
            flash("Cet email est déjà utilisé.", "danger")
            return render_template("auth/profile.html", form=form)
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Profil mis à jour.", "success")
        return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form)

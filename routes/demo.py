from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from extensions import db
from forms.upload import UploadForm
from models import Order
from services.auth_flow_demo import build_flow_status
from services.demo_service import demo_flag
from utils.decorators import admin_required
from utils.logging import log_event

demo_bp = Blueprint("demo", __name__, url_prefix="/demo")


@demo_bp.route("/")
@login_required
@admin_required
def index():
    flags = {flag: current_app.config.get(flag, False) for flag in (
        "ENABLE_SQLI",
        "ENABLE_XSS",
        "ENABLE_IDOR",
        "ENABLE_UPLOAD",
        "ENABLE_BRUTE_FORCE",
        "ENABLE_DEBUG_ERRORS",
        "ENABLE_ENUMERATION",
        "ENABLE_RATE_LIMITING",
        "ENABLE_CSRF",
        "ENABLE_INSECURE_COOKIES",
        "ENABLE_WEAK_HEADERS",
    )}
    return render_template("demo/index.html", flags=flags)


@demo_bp.route("/upload", methods=["GET", "POST"])
@login_required
@admin_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        upload_dir = Path(current_app.instance_path) / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        uploaded_file = form.file.data
        filename = secure_filename(getattr(uploaded_file, "filename", "") or "upload.bin")
        if not demo_flag("ENABLE_UPLOAD"):
            allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".txt"}
            if Path(filename).suffix.lower() not in allowed_extensions:
                flash("Type de fichier non autorisé.", "danger")
                return render_template("demo/upload.html", form=form)
        destination = upload_dir / filename
        uploaded_file.save(destination)
        log_event(current_app.logger, f"upload:{filename}")
        flash("Fichier téléversé.", "success")
        return redirect(url_for("demo.upload"))
    return render_template("demo/upload.html", form=form)


@demo_bp.route("/error")
@login_required
@admin_required
def error():
    if not demo_flag("ENABLE_DEBUG_ERRORS"):
        abort(404)
    raise RuntimeError("Demo error triggered")


@demo_bp.route("/auth-flow")
@login_required
def auth_flow():
    status = build_flow_status(
        app_config=current_app.config,
        session_data=session,
        authenticated=current_user.is_authenticated,
    )
    return render_template("demo/auth_flow.html", status=status)


@demo_bp.route("/idor/orders/<int:order_id>")
@login_required
def idor_order(order_id: int):
    order = db.session.get(Order, order_id)
    if not order:
        abort(404)
    if not demo_flag("ENABLE_IDOR") and order.user_id != current_user.id and not current_user.is_admin:
        abort(404)
    return render_template("orders/detail.html", order=order)

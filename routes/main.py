from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for, current_app

from forms.contact import ContactForm
from utils.logging import log_event

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        log_event(current_app.logger, "contact_message")
        flash("Votre message a été envoyé.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)

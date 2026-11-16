import secrets

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .models import User, db

bp = Blueprint("auth", __name__)


def _client_key() -> str:
    return request.remote_addr or "desconhecido"


def _new_csrf() -> str:
    return secrets.token_urlsafe(32)


def _next_url() -> str:
    target = request.args.get("next") or request.form.get("next") or ""
    if target.startswith("/") and not target.startswith("//"):
        return target
    return url_for("views.home")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("views.home"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        limiter = current_app.extensions["login_limiter"]
        client = _client_key()

        if limiter.is_blocked(client):
            flash("Muitas tentativas de login. Aguarde alguns minutos e tente de novo.", "error")
            return render_template("auth/login.html", email=email), 429

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            limiter.register_failure(client)
            flash("E-mail ou senha incorretos.", "error")
            return render_template("auth/login.html", email=email), 401

        limiter.clear(client)
        session.clear()
        session.permanent = True
        session["user_id"] = user.id
        session["_csrf"] = _new_csrf()
        if user.onboarding_done:
            return redirect(_next_url())
        return redirect(url_for("views.onboarding"))

    return render_template("auth/login.html", email="")


@bp.route("/registrar", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("views.home"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""
        errors = []

        if len(name) < 2:
            errors.append("Escreva seu nome.")
        if "@" not in email or "." not in email.split("@")[-1]:
            errors.append("Informe um e-mail válido.")
        if len(password) < 8:
            errors.append("A senha precisa ter pelo menos 8 caracteres.")
        if password != confirm:
            errors.append("As duas senhas não são iguais.")
        if User.query.filter_by(email=email).first():
            errors.append("Já existe uma conta com este e-mail.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("auth/register.html", name=name, email=email), 400

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

        session.clear()
        session.permanent = True
        session["user_id"] = user.id
        session["_csrf"] = _new_csrf()
        return redirect(url_for("views.onboarding"))

    return render_template("auth/register.html", name="", email="")


@bp.post("/sair")
def logout():
    session.clear()
    flash("Até logo. Cuide-se bem.", "info")
    return redirect(url_for("auth.login"))

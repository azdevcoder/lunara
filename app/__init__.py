import secrets
from datetime import date, timedelta

from flask import Flask, abort, g, request, send_from_directory, session

from config import Config
from .models import User, db

MONTHS_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]
MONTHS_SHORT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
WEEKDAYS_PT = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
WEEKDAYS_SHORT = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.config["TRUST_PROXY"]:
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    from .ratelimit import AttemptTracker

    app.extensions["login_limiter"] = AttemptTracker(
        max_attempts=app.config["LOGIN_MAX_ATTEMPTS"],
        window_seconds=app.config["LOGIN_WINDOW_SECONDS"],
    )

    db.init_app(app)

    from . import auth, views
    app.register_blueprint(auth.bp)
    app.register_blueprint(views.bp)

    @app.before_request
    def load_user():
        uid = session.get("user_id")
        g.user = db.session.get(User, uid) if uid else None

    @app.before_request
    def csrf_protect():
        if request.method == "POST":
            token = session.get("_csrf")
            sent = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
            if not token or not sent or not secrets.compare_digest(token, sent):
                abort(400, description="Sessão expirada. Recarregue a página e tente novamente.")

    def csrf_token() -> str:
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_urlsafe(32)
        return session["_csrf"]

    app.jinja_env.globals.update(
        csrf_token=csrf_token,
        today=date.today,
        timedelta=timedelta,
        MONTHS_PT=MONTHS_PT,
        WEEKDAYS_PT=WEEKDAYS_PT,
    )

    @app.context_processor
    def inject_globals():
        return {
            "current_user": g.get("user"),
            "now_year": date.today().year,
        }

    @app.template_filter("date_pt")
    def date_pt(value, style="short"):
        if not value:
            return ""
        if style == "long":
            return f"{value.day} de {MONTHS_PT[value.month - 1]} de {value.year}"
        if style == "full":
            return f"{WEEKDAYS_PT[value.weekday()]}, {value.day} de {MONTHS_PT[value.month - 1]}"
        if style == "month":
            return f"{MONTHS_PT[value.month - 1]} de {value.year}"
        if style == "weekday":
            return WEEKDAYS_SHORT[value.weekday()]
        return f"{value.day:02d} {MONTHS_SHORT[value.month - 1]}"

    @app.template_filter("month_name")
    def month_name(value):
        return MONTHS_PT[value - 1] if 1 <= value <= 12 else ""

    @app.template_filter("initials")
    def initials(value):
        return "".join(part[0] for part in str(value).split()[:2]).upper()

    @app.route("/healthz")
    def healthz():
        """Sinal de vida para systemd/nginx (não toca no banco)."""
        return "ok", 200, {"Content-Type": "text/plain; charset=utf-8"}

    @app.route("/sw.js")
    def service_worker():
        response = send_from_directory(app.static_folder, "sw.js", mimetype="application/javascript")
        response.headers["Service-Worker-Allowed"] = "/"
        response.headers["Cache-Control"] = "no-cache"
        return response

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        return response

    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(400)
    def bad_request(error):
        from flask import render_template
        return render_template("errors/400.html", message=getattr(error, "description", "")), 400

    return app

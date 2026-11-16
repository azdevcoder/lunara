import csv
import io
import json
from collections import Counter
from datetime import date, datetime, timedelta

from flask import (
    Blueprint, Response, abort, flash, g, redirect, render_template, request, url_for,
)
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from .content import (
    ARTICLES, DAILY_INSIGHTS, DISCHARGE_OPTIONS, FLOW_OPTIONS, GOALS,
    MOODS, MOODS_MAP, SEX_OPTIONS, SYMPTOMS, SYMPTOMS_MAP,
)
from .cycle import (
    FLOW_LEVELS, add_months, build_stats, day_status, gestation, month_weeks,
)
from .models import DailyLog, User, db

bp = Blueprint("views", __name__)


# ---------------------------------------------------------------- helpers

def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.user:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _all_logs(user):
    return (
        DailyLog.query.filter_by(user_id=user.id)
        .order_by(DailyLog.log_date.asc())
        .all()
    )


def _log_for(user, day):
    return DailyLog.query.filter_by(user_id=user.id, log_date=day).first()


def _get_or_create_log(user, day):
    log = _log_for(user, day)
    if log is None:
        log = DailyLog(user_id=user.id, log_date=day, symptoms=[], moods=[])
        db.session.add(log)
    return log


def _sync_last_period(user):
    """Mantém o perfil alinhado ao primeiro dia do fluxo mais recente."""
    flow_dates = [
        row.log_date
        for row in DailyLog.query.filter(
            DailyLog.user_id == user.id,
            DailyLog.flow.isnot(None),
            DailyLog.flow != "none",
        ).order_by(DailyLog.log_date.desc())
    ]
    if not flow_dates:
        user.last_period_start = None
        return

    start = flow_dates[0]
    for previous in flow_dates[1:]:
        if (start - previous).days > 2:
            break
        start = previous
    user.last_period_start = start


def _float(value):
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def _int(value, minimum=None, maximum=None):
    if value in (None, ""):
        return None
    try:
        number = int(value)
    except ValueError:
        return None
    if minimum is not None:
        number = max(minimum, number)
    if maximum is not None:
        number = min(maximum, number)
    return number


def _seed_period(user, start, length):
    """Cria registros de fluxo para um período informado, sem sobrescrever dados."""
    if not start:
        return
    for offset in range(max(1, min(length, 10))):
        day = start + timedelta(days=offset)
        if day > date.today():
            break
        log = _log_for(user, day)
        if log is None:
            log = DailyLog(user_id=user.id, log_date=day, symptoms=[], moods=[])
            db.session.add(log)
        if not log.flow:
            log.flow = "medium" if offset < 2 else "light"


def _latest_flow_start(user):
    row = (
        DailyLog.query.filter(
            DailyLog.user_id == user.id,
            DailyLog.flow.isnot(None),
            DailyLog.flow != "none",
        )
        .order_by(DailyLog.log_date.desc())
        .first()
    )
    return row.log_date if row else None


def _stats(user):
    logs = _all_logs(user)
    return logs, build_stats(user, logs)


def _daily_insight(stats):
    entries = DAILY_INSIGHTS.get(stats.phase) or DAILY_INSIGHTS["unknown"]
    index = (stats.cycle_day or 1) % len(entries)
    title, text = entries[index]
    return {"title": title, "text": text}


def _cycle_history(stats):
    rows = []
    episodes = stats.episodes
    for index in range(len(episodes) - 1, -1, -1):
        episode = episodes[index]
        length = None
        if index + 1 < len(episodes):
            length = (episodes[index + 1]["start"] - episode["start"]).days
        rows.append({
            "start": episode["start"],
            "end": episode["end"],
            "period_length": episode["length"],
            "cycle_length": length,
        })
    return rows


# ---------------------------------------------------------------- onboarding

@bp.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding():
    if g.user.onboarding_done:
        return redirect(url_for("views.home"))

    if request.method == "POST":
        user = g.user
        name = (request.form.get("name") or "").strip()
        birth = _parse_date(request.form.get("birth_date"))
        goal = request.form.get("goal") or "ciclo"
        last_period = _parse_date(request.form.get("last_period_start"))
        cycle_length = _int(request.form.get("cycle_length"), 21, 45) or 28
        period_length = _int(request.form.get("period_length"), 2, 10) or 5

        errors = []
        if len(name) < 2:
            errors.append("Como podemos te chamar?")
        if not last_period:
            errors.append("Informe o primeiro dia da sua última menstruação.")
        elif last_period > date.today():
            errors.append("A data da última menstruação não pode estar no futuro.")
        if goal not in {key for key, _, _, _ in GOALS}:
            errors.append("Escolha um objetivo.")
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "onboarding.html", goals=GOALS,
                form=request.form, birth=request.form.get("birth_date"),
            ), 400

        user.name = name
        user.birth_date = birth
        user.goal = goal
        user.last_period_start = last_period
        user.cycle_length = cycle_length
        user.period_length = period_length
        user.onboarding_done = True
        if goal == "gestacao":
            user.pregnancy_mode = True
            if not user.due_date and last_period:
                user.due_date = last_period + timedelta(days=280)
        _seed_period(user, last_period, period_length)
        db.session.commit()
        flash(f"Tudo pronto, {user.first_name()}! Seu ciclo começa a ganhar forma agora.", "success")
        return redirect(url_for("views.home"))

    return render_template("onboarding.html", goals=GOALS, form={}, birth="")


# ---------------------------------------------------------------- home

@bp.route("/")
@login_required
def home():
    if not g.user.onboarding_done:
        return redirect(url_for("views.onboarding"))

    logs, stats = _stats(g.user)
    log_map = {log.log_date: log for log in logs}
    today = date.today()
    today_log = log_map.get(today)
    insight = _daily_insight(stats)

    week = []
    for offset in range(7):
        day = today + timedelta(days=offset)
        week.append({
            "date": day,
            "status": day_status(day, stats),
            "log": log_map.get(day),
            "is_today": offset == 0,
        })

    upcoming = []
    for prediction in stats.predicted_periods:
        if prediction["start"] >= today:
            upcoming.append(
                {
                    "kind": "period",
                    "date": prediction["start"],
                    "end": prediction["end"],
                    "days": (prediction["start"] - today).days,
                }
            )
        if prediction["ovulation"] >= today:
            upcoming.append(
                {
                    "kind": "ovulation",
                    "date": prediction["ovulation"],
                    "days": (prediction["ovulation"] - today).days,
                }
            )
    upcoming.sort(key=lambda event: event["date"])
    upcoming = upcoming[:6]

    articles = ARTICLES[:3]
    water_pct = min(100, round(((today_log.water_ml if today_log else 0) or 0) / 2000 * 100))
    pregnancy = gestation(g.user.due_date, today) if g.user.pregnancy_mode and g.user.due_date else None

    streak = 0
    cursor = today
    while cursor in log_map and (log_map[cursor].flow or log_map[cursor].symptoms or log_map[cursor].moods or log_map[cursor].notes):
        streak += 1
        cursor -= timedelta(days=1)

    recent_moods = today_log.mood_list() if today_log else []

    return render_template(
        "home.html",
        stats=stats,
        today_log=today_log,
        insight=insight,
        week=week,
        upcoming=upcoming,
        articles=articles,
        water_pct=water_pct,
        pregnancy=pregnancy,
        streak=streak,
        recent_moods=recent_moods,
        moods=MOODS,
    )


@bp.post("/quick/water")
@login_required
def quick_water():
    delta = _int(request.form.get("delta"), -1000, 1000) or 250
    log = _get_or_create_log(g.user, date.today())
    log.water_ml = max(0, min(6000, (log.water_ml or 0) + delta))
    db.session.commit()
    return redirect(request.form.get("next") or url_for("views.home"))


@bp.post("/quick/mood")
@login_required
def quick_mood():
    mood = request.form.get("mood")
    if mood not in MOODS_MAP:
        abort(400)
    log = _get_or_create_log(g.user, date.today())
    moods = list(log.mood_list())
    if mood in moods:
        moods.remove(mood)
    else:
        moods.append(mood)
    log.moods = moods
    db.session.commit()
    return redirect(request.form.get("next") or url_for("views.home"))


@bp.post("/quick/pill")
@login_required
def quick_pill():
    log = _get_or_create_log(g.user, date.today())
    log.pill_taken = not bool(log.pill_taken)
    db.session.commit()
    return redirect(request.form.get("next") or url_for("views.home"))


@bp.post("/periodo/iniciar")
@login_required
def period_start():
    log = _get_or_create_log(g.user, date.today())
    log.flow = "medium"
    g.user.last_period_start = date.today()
    db.session.commit()
    flash("Período registrado hoje. As previsões foram atualizadas.", "success")
    return redirect(url_for("views.home"))


@bp.route("/ciclo/novo", methods=["GET", "POST"])
@login_required
def new_cycle():
    if request.method == "POST":
        start = _parse_date(request.form.get("start"))
        period_length = _int(request.form.get("period_length"), 2, 10)
        cycle_length = _int(request.form.get("cycle_length"), 21, 45)
        errors = []
        if not start:
            errors.append("Informe o primeiro dia da menstruação.")
        elif start > date.today():
            errors.append("O primeiro dia não pode estar no futuro.")
        if not period_length:
            errors.append("Escolha quantos dias a menstruação dura.")
        if not cycle_length:
            errors.append("Escolha a duração média do ciclo.")
        if errors:
            for message in errors:
                flash(message, "error")
            return (
                render_template(
                    "new_cycle.html", form=request.form, latest_flow=_latest_flow_start(g.user)
                ),
                400,
            )

        previous_latest = _latest_flow_start(g.user)
        g.user.period_length = period_length
        g.user.cycle_length = cycle_length
        _seed_period(g.user, start, period_length)
        if previous_latest is None or start >= previous_latest:
            g.user.last_period_start = start
        db.session.commit()

        stats = build_stats(g.user, _all_logs(g.user), today=date.today())
        if previous_latest and start < previous_latest:
            flash(
                f"Fluxo adicionado a partir de {start:%d/%m}. O ciclo atual continua "
                f"contando de {previous_latest:%d/%m}.",
                "info",
            )
        next_period = f"{stats.next_period:%d/%m}" if stats.next_period else "—"
        flash(
            f"Ciclo registrado: {period_length} dias de fluxo e ciclo de {cycle_length} dias. "
            f"Próximo período previsto para {next_period}.",
            "success",
        )
        return redirect(url_for("views.calendar_view", mes=start.strftime("%Y-%m")))

    return render_template(
        "new_cycle.html",
        form={
            "start": date.today().isoformat(),
            "period_length": g.user.period_length or 5,
            "cycle_length": g.user.cycle_length or 28,
        },
        latest_flow=_latest_flow_start(g.user),
    )


# ---------------------------------------------------------------- calendar

@bp.route("/calendario")
@login_required
def calendar_view():
    today = date.today()
    month_value = request.args.get("mes") or f"{today.year}-{today.month:02d}"
    try:
        year, month = [int(part) for part in month_value.split("-")[:2]]
        if not (1 <= month <= 12 and 2000 <= year <= 2100):
            raise ValueError
    except (ValueError, TypeError):
        year, month = today.year, today.month

    logs, stats = _stats(g.user)
    log_map = {log.log_date: log for log in logs}
    weeks = month_weeks(year, month)
    days = []
    for week in weeks:
        row = []
        for day in week:
            row.append({
                "date": day,
                "in_month": day.month == month,
                "is_today": day == today,
                "status": day_status(day, stats),
                "log": log_map.get(day),
            })
        days.append(row)

    anchor = date(year, month, 1)
    prev_month = add_months(anchor, -1)
    next_month = add_months(anchor, 1)
    month_logs = [log for log in logs if log.log_date.year == year and log.log_date.month == month]
    flow_days = sum(1 for log in month_logs if log.flow and log.flow != "none")
    symptom_days = sum(1 for log in month_logs if log.symptom_list())

    return render_template(
        "calendar.html",
        stats=stats,
        weeks=days,
        year=year,
        month=month,
        anchor=anchor,
        prev_month=prev_month,
        next_month=next_month,
        month_logs=month_logs,
        flow_days=flow_days,
        symptom_days=symptom_days,
    )


# ---------------------------------------------------------------- daily log

@bp.route("/registro/<day_value>", methods=["GET", "POST"])
@login_required
def log_day(day_value):
    day = _parse_date(day_value)
    if not day:
        abort(404)
    if day > date.today():
        flash("Você pode registrar até hoje. Escolha uma data passada.", "info")
        return redirect(url_for("views.log_day", day_value=date.today().isoformat()))

    log = _log_for(g.user, day)

    if request.method == "POST":
        log = log or DailyLog(user_id=g.user.id, log_date=day, symptoms=[], moods=[])
        if log.id is None:
            db.session.add(log)

        flow = request.form.get("flow") or "none"
        log.flow = flow if flow in FLOW_LEVELS or flow == "none" else None
        log.symptoms = [item for item in request.form.getlist("symptoms") if item in SYMPTOMS_MAP]
        log.moods = [item for item in request.form.getlist("moods") if item in MOODS_MAP]
        log.energy = _int(request.form.get("energy"), 1, 5)
        log.sleep_hours = _float(request.form.get("sleep_hours"))
        log.water_ml = _int(request.form.get("water_ml"), 0, 6000)
        log.weight_kg = _float(request.form.get("weight_kg"))
        log.temperature = _float(request.form.get("temperature"))
        log.sex = request.form.get("sex") or None
        log.discharge = request.form.get("discharge") or None
        log.cravings = (request.form.get("cravings") or "").strip() or None
        log.exercise = (request.form.get("exercise") or "").strip() or None
        log.medication = (request.form.get("medication") or "").strip() or None
        log.pill_taken = bool(request.form.get("pill_taken"))
        log.notes = (request.form.get("notes") or "").strip() or None

        db.session.flush()
        _sync_last_period(g.user)
        db.session.commit()
        flash("Registro salvo. Seu ciclo agradece. 🌙", "success")
        return redirect(url_for("views.calendar_view", mes=day.strftime("%Y-%m")))

    return render_template(
        "log.html",
        day=day,
        log=log,
        flow_options=FLOW_OPTIONS,
        symptoms=SYMPTOMS,
        moods=MOODS,
        sex_options=SEX_OPTIONS,
        discharge_options=DISCHARGE_OPTIONS,
    )


@bp.post("/registro/<day_value>/excluir")
@login_required
def delete_log(day_value):
    day = _parse_date(day_value)
    if not day:
        abort(404)
    log = _log_for(g.user, day)
    if log:
        db.session.delete(log)
        db.session.flush()
        _sync_last_period(g.user)
        db.session.commit()
        flash("Registro removido.", "info")
    return redirect(url_for("views.calendar_view", mes=day.strftime("%Y-%m")))


# ---------------------------------------------------------------- insights

@bp.route("/insights")
@login_required
def insights():
    logs, stats = _stats(g.user)
    today = date.today()
    cutoff = today - timedelta(days=120)
    recent = [log for log in logs if log.log_date >= cutoff]

    symptom_counter = Counter()
    mood_counter = Counter()
    flow_counter = Counter()
    for log in recent:
        symptom_counter.update(log.symptom_list())
        mood_counter.update(log.mood_list())
        if log.flow and log.flow != "none":
            flow_counter.update([log.flow])

    symptoms = [
        {"key": key, "label": SYMPTOMS_MAP[key][0], "emoji": SYMPTOMS_MAP[key][1], "count": count}
        for key, count in symptom_counter.most_common(8) if key in SYMPTOMS_MAP
    ]
    max_symptom = max([s["count"] for s in symptoms], default=1) or 1

    moods = [
        {"key": key, "label": MOODS_MAP[key][0], "emoji": MOODS_MAP[key][1], "count": count}
        for key, count in mood_counter.most_common() if key in MOODS_MAP
    ]
    max_mood = max([m["count"] for m in moods], default=1) or 1

    history = _cycle_history(stats)
    chart_cycles = [row for row in history[:8] if row["cycle_length"]][::-1]
    max_cycle = max([row["cycle_length"] for row in chart_cycles], default=35) or 35

    sleep_values = [log.sleep_hours for log in recent if log.sleep_hours]
    water_values = [log.water_ml for log in recent if log.water_ml]
    weight_values = [log for log in recent if log.weight_kg][-12:]

    avg_sleep = round(sum(sleep_values) / len(sleep_values), 1) if sleep_values else None
    avg_water = round(sum(water_values) / len(water_values)) if water_values else None
    log_days = len(recent)

    return render_template(
        "insights.html",
        stats=stats,
        symptoms=symptoms,
        max_symptom=max_symptom,
        moods=moods,
        max_mood=max_mood,
        flow_counter=flow_counter,
        history=history,
        chart_cycles=chart_cycles,
        max_cycle=max_cycle,
        avg_sleep=avg_sleep,
        avg_water=avg_water,
        weight_values=weight_values,
        log_days=log_days,
        symptom_days=sum(1 for log in recent if log.symptom_list()),
    )


# ---------------------------------------------------------------- pregnancy

@bp.route("/gestacao", methods=["GET", "POST"])
@login_required
def pregnancy():
    if request.method == "POST":
        due = _parse_date(request.form.get("due_date"))
        last_period = _parse_date(request.form.get("last_period"))
        if last_period and not due:
            due = last_period + timedelta(days=280)
        if not due:
            flash("Informe a data provável do parto ou o primeiro dia da última menstruação.", "error")
        else:
            g.user.due_date = due
            g.user.pregnancy_mode = True
            db.session.commit()
            flash("Modo gestação ativado.", "success")
            return redirect(url_for("views.pregnancy"))

    today = date.today()
    info = gestation(g.user.due_date, today) if g.user.due_date else None
    weeks = []
    if info:
        from .cycle import PREGNANCY_SIZES
        current = info["weeks"]
        for week in range(max(4, current - 2), min(40, current + 4) + 1):
            size = PREGNANCY_SIZES.get(week)
            if size:
                weeks.append({"week": week, "size": size, "current": week == current})
    return render_template("pregnancy.html", info=info, weeks=weeks)


# ---------------------------------------------------------------- content

@bp.route("/artigos")
@login_required
def articles():
    category = request.args.get("categoria") or ""
    items = ARTICLES
    if category:
        items = [article for article in ARTICLES if article["category"] == category]
    categories = sorted({article["category"] for article in ARTICLES})
    return render_template("articles.html", articles=items, categories=categories, selected=category)


@bp.route("/artigos/<slug>")
@login_required
def article(slug):
    item = next((article for article in ARTICLES if article["slug"] == slug), None)
    if not item:
        abort(404)
    related = [article for article in ARTICLES if article["category"] == item["category"] and article["slug"] != slug][:3]
    return render_template("article.html", article=item, related=related)


# ---------------------------------------------------------------- profile

@bp.route("/perfil", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        action = request.form.get("action")
        user = g.user

        if action == "profile":
            name = (request.form.get("name") or "").strip()
            email = (request.form.get("email") or "").strip().lower()
            birth = _parse_date(request.form.get("birth_date"))
            goal = request.form.get("goal") or user.goal
            if len(name) < 2:
                flash("Escreva seu nome.", "error")
            elif "@" not in email:
                flash("Informe um e-mail válido.", "error")
            elif User.query.filter(User.email == email, User.id != user.id).first():
                flash("Este e-mail já está em uso.", "error")
            else:
                user.name = name
                user.email = email
                user.birth_date = birth
                if goal in {key for key, _, _, _ in GOALS}:
                    user.goal = goal
                db.session.commit()
                flash("Perfil atualizado.", "success")

        elif action == "cycle":
            cycle_length = _int(request.form.get("cycle_length"), 21, 45)
            period_length = _int(request.form.get("period_length"), 2, 10)
            last_period = _parse_date(request.form.get("last_period_start"))
            if cycle_length:
                user.cycle_length = cycle_length
            if period_length:
                user.period_length = period_length
            if last_period and last_period <= date.today():
                user.last_period_start = last_period
                if request.form.get("seed_period"):
                    _seed_period(user, last_period, period_length or user.period_length)
            db.session.commit()
            flash("Configurações do ciclo atualizadas.", "success")

        elif action == "reminders":
            user.notifications_enabled = bool(request.form.get("notifications_enabled"))
            reminder = request.form.get("reminder_time") or "09:00"
            user.reminder_time = reminder[:5]
            db.session.commit()
            flash("Lembretes atualizados.", "success")

        elif action == "contraceptive":
            user.contraceptive = (request.form.get("contraceptive") or "").strip() or None
            user.contraceptive_time = (request.form.get("contraceptive_time") or "21:00")[:5]
            db.session.commit()
            flash("Lembrete de contraceptivo salvo.", "success")

        elif action == "pregnancy":
            user.pregnancy_mode = bool(request.form.get("pregnancy_mode"))
            due = _parse_date(request.form.get("due_date"))
            if due:
                user.due_date = due
            if user.pregnancy_mode and not user.due_date:
                flash("Informe a data provável do parto para ativar o modo gestação.", "error")
                user.pregnancy_mode = False
            db.session.commit()
            flash("Modo gestação atualizado.", "success")

        elif action == "password":
            current = request.form.get("current_password") or ""
            new = request.form.get("new_password") or ""
            confirm = request.form.get("confirm_password") or ""
            if not check_password_hash(user.password_hash, current):
                flash("A senha atual não confere.", "error")
            elif len(new) < 8:
                flash("A nova senha precisa ter pelo menos 8 caracteres.", "error")
            elif new != confirm:
                flash("A confirmação não confere.", "error")
            else:
                user.password_hash = generate_password_hash(new)
                db.session.commit()
                flash("Senha alterada.", "success")

        elif action == "theme":
            theme = request.form.get("theme") or "rose"
            if theme in {"rose", "lavender", "sage", "midnight"}:
                user.theme = theme
                db.session.commit()
                flash("Tema aplicado.", "success")

        elif action == "delete":
            password = request.form.get("confirm_password") or ""
            confirmation = (request.form.get("confirmation") or "").strip()
            if confirmation != "EXCLUIR":
                flash("Digite EXCLUIR para confirmar.", "error")
            elif not check_password_hash(user.password_hash, password):
                flash("Senha incorreta.", "error")
            else:
                db.session.delete(user)
                db.session.commit()
                from flask import session
                session.clear()
                flash("Sua conta e seus dados foram apagados.", "info")
                return redirect(url_for("auth.register"))

        return redirect(url_for("views.profile"))

    logs, stats = _stats(g.user)
    today = date.today()
    return render_template(
        "profile.html",
        stats=stats,
        goals=GOALS,
        total_logs=len(logs),
        total_periods=len(stats.episodes),
        log_today=_log_for(g.user, today),
    )


# ---------------------------------------------------------------- export

@bp.route("/exportar.json")
@login_required
def export_json():
    logs, stats = _stats(g.user)
    payload = {
        "app": "Lunara",
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "profile": {
            "name": g.user.name,
            "email": g.user.email,
            "birth_date": g.user.birth_date.isoformat() if g.user.birth_date else None,
            "goal": g.user.goal,
            "cycle_length": g.user.cycle_length,
            "period_length": g.user.period_length,
            "last_period_start": g.user.last_period_start.isoformat() if g.user.last_period_start else None,
            "pregnancy_mode": g.user.pregnancy_mode,
            "due_date": g.user.due_date.isoformat() if g.user.due_date else None,
        },
        "summary": {
            "average_cycle": stats.avg_cycle,
            "average_period": stats.avg_period,
            "regularity": stats.regularity,
            "cycles_tracked": len(stats.episodes),
        },
        "logs": [
            {
                "date": log.log_date.isoformat(),
                "flow": log.flow,
                "symptoms": log.symptom_list(),
                "moods": log.mood_list(),
                "energy": log.energy,
                "sleep_hours": log.sleep_hours,
                "water_ml": log.water_ml,
                "weight_kg": log.weight_kg,
                "temperature": log.temperature,
                "sex": log.sex,
                "discharge": log.discharge,
                "cravings": log.cravings,
                "exercise": log.exercise,
                "medication": log.medication,
                "pill_taken": bool(log.pill_taken),
                "notes": log.notes,
            }
            for log in logs
        ],
    }
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    filename = f"lunara-{date.today().isoformat()}.json"
    return Response(
        body,
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@bp.route("/exportar.csv")
@login_required
def export_csv():
    logs, _ = _stats(g.user)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow([
        "data", "fluxo", "sintomas", "humores", "energia", "sono_horas", "agua_ml",
        "peso_kg", "temperatura", "sexo", "secrecao", "desejos", "exercicio",
        "medicacao", "pilula_tomada", "notas",
    ])
    for log in logs:
        writer.writerow([
            log.log_date.isoformat(),
            log.flow or "",
            ", ".join(SYMPTOMS_MAP.get(item, (item,))[0] for item in log.symptom_list()),
            ", ".join(MOODS_MAP.get(item, (item,))[0] for item in log.mood_list()),
            log.energy or "",
            log.sleep_hours or "",
            log.water_ml or "",
            log.weight_kg or "",
            log.temperature or "",
            log.sex or "",
            log.discharge or "",
            log.cravings or "",
            log.exercise or "",
            log.medication or "",
            "sim" if log.pill_taken else "não",
            log.notes or "",
        ])
    body = "\ufeff" + buffer.getvalue()
    filename = f"lunara-{date.today().isoformat()}.csv"
    return Response(
        body,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@bp.route("/offline")
def offline():
    return render_template("offline.html")


@bp.route("/saude")
def health():
    return {"status": "ok", "app": "Lunara"}

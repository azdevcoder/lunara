"""Motor de previsão do ciclo menstrual.

A fonte de verdade são os registros diários com fluxo. Episódios de fluxo
consecutivos (com até 2 dias de intervalo) formam um período; cada início de
período marca o começo de um novo ciclo.
"""
from __future__ import annotations

import calendar as _calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from statistics import mean, pstdev

FLOW_LEVELS = {"spotting": 1, "light": 2, "medium": 3, "heavy": 4}
FLOW_LABELS = {
    "spotting": "Escape",
    "light": "Leve",
    "medium": "Médio",
    "heavy": "Intenso",
}

PHASES = {
    "menstrual": {
        "label": "Fase menstrual",
        "short": "Menstruação",
        "emoji": "moon",
        "color": "#d94f70",
        "description": "Seu corpo está renovando. Priorize descanso, calor e ferro.",
    },
    "follicular": {
        "label": "Fase folicular",
        "short": "Folicular",
        "emoji": "seedling",
        "color": "#7aa88a",
        "description": "Energia subindo. Bom momento para começar coisas novas.",
    },
    "ovulatory": {
        "label": "Fase ovulatória",
        "short": "Ovulação",
        "emoji": "sparkles",
        "color": "#c98a3f",
        "description": "Pico de energia e sociabilidade. A janela fértil está aberta.",
    },
    "luteal": {
        "label": "Fase lútea",
        "short": "Lútea",
        "emoji": "leaf",
        "color": "#9a7bb8",
        "description": "A progesterona sobe. Autocuidado e sono importam mais agora.",
    },
    "unknown": {
        "label": "Sem dados suficientes",
        "short": "—",
        "emoji": "flower",
        "color": "#c9a6b8",
        "description": "Registre seu período para começarmos as previsões.",
    },
}


@dataclass
class CycleStats:
    episodes: list[dict] = field(default_factory=list)
    cycle_lengths: list[int] = field(default_factory=list)
    avg_cycle: int = 28
    avg_period: int = 5
    variation: int = 0
    regularity: str = "Coletando dados"
    regularity_score: int = 0
    current_start: date | None = None
    current_period_end: date | None = None
    cycle_day: int = 1
    next_period: date | None = None
    ovulation: date | None = None
    fertile_start: date | None = None
    fertile_end: date | None = None
    pms_start: date | None = None
    phase: str = "unknown"
    phase_label: str = "Sem dados suficientes"
    phase_description: str = ""
    days_until_period: int | None = None
    late_days: int = 0
    predicted_periods: list[dict] = field(default_factory=list)
    actual_flow_dates: set = field(default_factory=set)
    is_period_today: bool = False
    cycle_progress: float = 0.0

    @property
    def phase_data(self):
        return PHASES.get(self.phase, PHASES["unknown"])

    @property
    def has_data(self):
        return self.current_start is not None


def _episodes(logs):
    flow_dates = sorted({log.log_date for log in logs if log.flow in FLOW_LEVELS})
    if not flow_dates:
        return [], set(flow_dates)

    groups: list[list[date]] = []
    current = [flow_dates[0]]
    for day in flow_dates[1:]:
        if (day - current[-1]).days <= 2:
            current.append(day)
        else:
            groups.append(current)
            current = [day]
    groups.append(current)

    episodes = []
    for group in groups:
        length = (group[-1] - group[0]).days + 1
        if length > 15:
            # Um "período" longo demais provavelmente são registros esparsos.
            length = min(length, 15)
        episodes.append({"start": group[0], "end": group[-1], "length": length})
    return episodes, set(flow_dates)


def build_stats(user, logs, today: date | None = None) -> CycleStats:
    today = today or date.today()
    stats = CycleStats()
    episodes, flow_dates = _episodes(logs)
    stats.episodes = episodes
    stats.actual_flow_dates = flow_dates

    default_cycle = max(15, min(60, user.cycle_length or 28))
    default_period = max(1, min(12, user.period_length or 5))

    if len(episodes) >= 2:
        history = episodes
        # O período atual pode estar em curso: nesse caso ele não entra na média.
        if today < episodes[-1]["start"] + timedelta(days=default_period):
            history = episodes[:-1]
    else:
        history = []

    if len(history) >= 2:
        stats.avg_period = round(mean([e["length"] for e in history[-6:]]))
        stats.avg_period = max(1, min(12, stats.avg_period))
    else:
        # Com poucos períodos completos, a duração informada no perfil vale mais
        # do que o trecho já registrado — inclusive quando o fluxo ainda está em curso.
        stats.avg_period = default_period

    cycle_lengths = []
    for prev, nxt in zip(episodes, episodes[1:]):
        diff = (nxt["start"] - prev["start"]).days
        if 15 <= diff <= 70:
            cycle_lengths.append(diff)
    stats.cycle_lengths = cycle_lengths

    if len(cycle_lengths) >= 2:
        last = cycle_lengths[-6:]
        stats.avg_cycle = round(mean(last))
        stats.variation = max(last) - min(last)
        sd = pstdev(last) if len(last) > 1 else 0
        if sd <= 1.5:
            stats.regularity = "Muito regular"
            stats.regularity_score = 96
        elif sd <= 3:
            stats.regularity = "Regular"
            stats.regularity_score = 82
        elif sd <= 5:
            stats.regularity = "Leve variação"
            stats.regularity_score = 62
        else:
            stats.regularity = "Irregular"
            stats.regularity_score = 38
    else:
        # Com menos de três períodos, a duração informada vale mais que um único
        # intervalo — inclusive quando o ciclo atual acabou de ser registrado.
        stats.avg_cycle = default_cycle
        stats.regularity = "Coletando dados"
        stats.regularity_score = 40

    known_start = episodes[-1]["start"] if episodes else user.last_period_start
    if known_start:
        stats.current_start = known_start
        stats.current_period_end = known_start + timedelta(days=default_period - 1)
        stats.cycle_day = max(1, (today - known_start).days + 1)
        stats.next_period = known_start + timedelta(days=stats.avg_cycle)
        stats.ovulation = stats.next_period - timedelta(days=14)
        stats.fertile_start = stats.ovulation - timedelta(days=5)
        stats.fertile_end = stats.ovulation + timedelta(days=1)
        stats.pms_start = stats.next_period - timedelta(days=5)
        stats.days_until_period = (stats.next_period - today).days
        stats.late_days = max(0, -stats.days_until_period)
        stats.is_period_today = today in flow_dates
        stats.cycle_progress = min(1.0, max(0.0, stats.cycle_day / stats.avg_cycle))

        expected_ovulation = known_start + timedelta(days=stats.avg_cycle - 14)
        if stats.cycle_day <= stats.avg_period:
            stats.phase = "menstrual"
        elif stats.cycle_day < (expected_ovulation - known_start).days:
            stats.phase = "follicular"
        elif stats.cycle_day <= (expected_ovulation - known_start).days + 1:
            stats.phase = "ovulatory"
        else:
            stats.phase = "luteal"
        stats.phase_label = PHASES[stats.phase]["label"]
        stats.phase_description = PHASES[stats.phase]["description"]

    # Previsões para os próximos meses (e para o mês corrente, se atrasado).
    if stats.next_period:
        start = stats.next_period
        # Se a previsão já passou muito, avança até perto de hoje para o calendário.
        while start < today - timedelta(days=stats.avg_cycle * 2):
            start += timedelta(days=stats.avg_cycle)
        for _ in range(8):
            stats.predicted_periods.append(
                {
                    "start": start,
                    "end": start + timedelta(days=max(2, stats.avg_period) - 1),
                    "ovulation": start - timedelta(days=14),
                    "fertile_start": start - timedelta(days=19),
                    "fertile_end": start - timedelta(days=13),
                    "pms_start": start - timedelta(days=5),
                }
            )
            start = start + timedelta(days=stats.avg_cycle)

    return stats


def day_status(day: date, stats: CycleStats) -> dict | None:
    """Retorna o destaque do dia para calendário e tira da semana."""
    if day in stats.actual_flow_dates:
        return {"kind": "period", "label": "Menstruação", "short": "Fluxo"}

    # Dias do fluxo atual que ainda não chegaram (o registro só existe até hoje).
    if (
        stats.current_start
        and stats.current_period_end
        and day >= date.today()
        and stats.current_start <= day <= stats.current_period_end
    ):
        return {"kind": "period-predicted", "label": "Menstruação prevista", "short": "Previsto"}

    for pred in stats.predicted_periods:
        if pred["start"] <= day <= pred["end"]:
            return {"kind": "period-predicted", "label": "Menstruação prevista", "short": "Previsto"}
        if day == pred["ovulation"]:
            return {"kind": "ovulation", "label": "Ovulação prevista", "short": "Ovulação"}
        if pred["fertile_start"] <= day <= pred["fertile_end"]:
            return {"kind": "fertile", "label": "Janela fértil", "short": "Fértil"}
        if pred["pms_start"] <= day < pred["start"]:
            return {"kind": "pms", "label": "TPM", "short": "TPM"}
    return None


def month_weeks(year: int, month: int) -> list[list[date]]:
    cal = _calendar.Calendar(firstweekday=0)
    return cal.monthdatescalendar(year, month)


def add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    last = _calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, last))


def gestation(due_date: date, today: date) -> dict:
    total = 280
    remaining = (due_date - today).days
    elapsed = total - remaining
    elapsed = max(0, min(total, elapsed))
    weeks = elapsed // 7
    days = elapsed % 7
    trimester = 1 if weeks < 13 else (2 if weeks < 27 else 3)
    progress = round((elapsed / total) * 100, 1)
    return {
        "weeks": weeks,
        "days": days,
        "remaining": max(0, remaining),
        "trimester": trimester,
        "progress": progress,
        "size": PREGNANCY_SIZES.get(weeks, PREGNANCY_SIZES[4]),
    }


_PREGNANCY_FRUITS = {
    4: ("semente de papoula", 0.1),
    5: ("semente de maçã", 0.2),
    6: ("mirtilo", 0.5),
    7: ("framboesa", 1.0),
    8: ("uva", 1.6),
    9: ("cereja", 2.3),
    10: ("morango", 3.1),
    11: ("azeitona", 4.1),
    12: ("limão", 5.4),
    13: ("pêssego", 7.4),
    14: ("limão siciliano", 8.7),
    15: ("maçã", 10.1),
    16: ("abacate", 11.6),
    17: ("pera", 13.0),
    18: ("batata-doce", 14.2),
    19: ("manga", 15.3),
    20: ("banana", 16.4),
    21: ("cenoura", 26.7),
    22: ("batata-doce grande", 27.8),
    23: ("manga grande", 28.9),
    24: ("espiga de milho", 30.0),
    25: ("couve-flor", 34.6),
    26: ("brócolis", 35.6),
    27: ("repolho", 36.6),
    28: ("berinjela", 37.6),
    29: ("abóbora pequena", 38.6),
    30: ("repolho grande", 39.9),
    31: ("coco", 41.1),
    32: ("acelga", 42.4),
    33: ("abacaxi", 43.7),
    34: ("melão", 45.0),
    35: ("melão grande", 46.2),
    36: ("alface romana", 47.4),
    37: ("acelga grande", 48.6),
    38: ("alho-poró", 49.8),
    39: ("melancia pequena", 50.7),
    40: ("abóbora", 51.2),
}


def _size_icon(week: int) -> str:
    """Ícone coerente com a fase da gestação (semente → folha → flor → coração → bebê)."""
    if week < 9:
        return "seedling"
    if week < 15:
        return "leaf"
    if week < 27:
        return "flower"
    if week < 34:
        return "heart"
    return "baby"


PREGNANCY_SIZES = {
    week: {"emoji": _size_icon(week), "name": name, "cm": cm}
    for week, (name, cm) in _PREGNANCY_FRUITS.items()
}

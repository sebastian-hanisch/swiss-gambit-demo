"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import sga_constants as C
import sga_evaluation as ev


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)", barmode="group")
    return lock_axes(fig)


def _seat_label(seat: int) -> str:
    return f"Platz {seat}"


def build_example(a: ev.Analysis):
    """Das Beispiel-Feld: oben die Punkte des Spielers nach jeder Runde, unten die Stärke des jeweiligen Gegners (Elo); ehrlich gegen Gambit."""
    rows = a.rows
    rounds = [f"Runde {r.round_no}" for r in rows]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, subplot_titles=("Punkte nach der Runde", "Stärke des Gegners (Elo)"))
    fig.add_trace(go.Scatter(x=rounds, y=[r.total_honest for r in rows], mode="lines+markers", name="ehrlich", line=dict(color=C.COLOR_HONEST, width=3),
                             hovertemplate="%{x}: %{y:.1f} Punkte<extra>ehrlich</extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=rounds, y=[r.total_gambit for r in rows], mode="lines+markers", name="Gambit", line=dict(color=C.COLOR_GAMBIT, width=3),
                             hovertemplate="%{x}: %{y:.1f} Punkte<extra>Gambit</extra>"), row=1, col=1)
    fig.add_trace(go.Bar(x=rounds, y=[r.elo_honest for r in rows], name="Gegner ehrlich", marker_color=C.COLOR_HONEST, showlegend=False,
                         hovertemplate="%{x}: Gegner %{y:.0f} Elo<extra>ehrlich</extra>"), row=2, col=1)
    fig.add_trace(go.Bar(x=rounds, y=[r.elo_gambit for r in rows], name="Gegner Gambit", marker_color=C.COLOR_GAMBIT, showlegend=False,
                         hovertemplate="%{x}: Gegner %{y:.0f} Elo<extra>Gambit</extra>"), row=2, col=1)
    lo = min(min(r.elo_honest, r.elo_gambit) for r in rows)
    hi = max(max(r.elo_honest, r.elo_gambit) for r in rows)
    fig.update_yaxes(range=[math.floor(lo / 50) * 50 - 50, math.ceil(hi / 50) * 50 + 50], row=2, col=1)
    fig.update_yaxes(title_text="Punkte", row=1, col=1)
    return _base(fig, height=480)


def build_main_places(cells: list[dict], highlight_seat: int | None = None):
    """Hauptmessreihe: mittlerer Endplatz je Setzplatz, ehrlich gegen Gambit (kleiner = besser). Der gewählte Setzplatz ist mit einem Stern markiert."""
    labels = [_seat_label(c["seat"]) + (" ★" if c["seat"] == highlight_seat else "") for c in cells]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[c["hp"] for c in cells], name="ehrlich", marker_color=C.COLOR_HONEST, hovertemplate="%{x}: Platz %{y:.2f}<extra>ehrlich</extra>"))
    fig.add_trace(go.Bar(x=labels, y=[c["gp"] for c in cells], name="Gambit", marker_color=C.COLOR_GAMBIT, hovertemplate="%{x}: Platz %{y:.2f}<extra>Gambit</extra>"))
    fig.update_yaxes(title_text="mittlerer Endplatz (kleiner = besser)")
    fig.update_xaxes(title_text="Setzplatz des Gambit-Spielers")
    return _base(fig)


def build_opponents(cells: list[dict], after: bool):
    """Mittlere Stärke der Gegner (Elo) je Setzplatz; `after`: nur die Runden nach der Gambit-Runde."""
    hk, gk = ("hopp_after", "gopp_after") if after else ("hopp", "gopp")
    labels = [_seat_label(c["seat"]) for c in cells]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[c[hk] for c in cells], name="Gegner ehrlich", marker_color=C.COLOR_HONEST, hovertemplate="%{x}: %{y:.0f} Elo<extra>ehrlich</extra>"))
    fig.add_trace(go.Bar(x=labels, y=[c[gk] for c in cells], name="Gegner mit Gambit", marker_color=C.COLOR_GAMBIT, hovertemplate="%{x}: %{y:.0f} Elo<extra>Gambit</extra>"))
    values = [c[k] for c in cells for k in (hk, gk)]
    fig.update_yaxes(title_text="mittlere Stärke der Gegner (Elo)", range=[math.floor(min(values) / 25) * 25 - 25, math.ceil(max(values) / 25) * 25 + 25])
    fig.update_xaxes(title_text="Setzplatz des Gambit-Spielers")
    return _base(fig, height=320)


def build_difference_hist(cell: dict):
    """Verteilung der Platzänderung (Gambit minus ehrlich) über die Felder einer Zelle: links = Gambit besser, rechts = schlechter."""
    centers = [C.HIST_LO + C.HIST_STEP * (i + 0.5) for i in range(C.HIST_BINS)]
    counts = cell["hist"]
    first = next(i for i, c in enumerate(counts) if c)
    last = max(i for i, c in enumerate(counts) if c)
    labels = [f"{centers[i]:+.0f}" if centers[i] else "0" for i in range(first, last + 1)]
    colors = [C.COLOR_HONEST if centers[i] < 0 else C.COLOR_NEUTRAL if centers[i] == 0 else C.COLOR_GAMBIT for i in range(first, last + 1)]
    fig = go.Figure(go.Bar(x=labels, y=counts[first:last + 1], marker_color=colors, hovertemplate="Platzänderung um %{x} (±1): %{y} Felder<extra></extra>"))
    fig.update_xaxes(title_text="Platzänderung, gerundet auf gerade Zahlen (Gambit minus ehrlich; negativ = Gambit besser)")
    fig.update_yaxes(title_text="Zahl der Felder")
    return _base(fig, height=300)


def build_sensitivity(cells: list[dict], axis: str):
    """Empfindlichkeitsreihe: mittlere Platzänderung (Gambit minus ehrlich) mit ±2 Standardfehlern, eine Linie je Setzplatz-Art (1, 4, 8, Feldmitte)."""
    if axis == "size":
        keys = [(n, r) for n in C.SENS_N for r in C.SENS_ROUNDS]
        label = lambda k: f"{k[0]} Sp., {k[1]} R."  # noqa: E731
        pick = lambda c: (c["n"], c["rounds"])  # noqa: E731
        title = "Feldgröße (Spieler), Rundenzahl"
    else:
        keys = list(C.SENS_SPREADS)
        label = lambda k: f"σ = {k}"  # noqa: E731
        pick = lambda c: c["spread"]  # noqa: E731
        title = "Elo-Streuung σ"
    fig = go.Figure()
    for slot, name in ((1, "Setzplatz 1"), (4, "Setzplatz 4"), (8, "Setzplatz 8"), (None, "Feldmitte (n/2)")):
        xs, ys, es = [], [], []
        for k in keys:
            for c in cells:
                is_mid = c["seat"] == c["n"] // 2 and c["seat"] not in C.SENS_SEAT_NS
                if pick(c) == k and ((slot is None and is_mid) or c["seat"] == slot):
                    xs.append(label(k))
                    ys.append(ev.d_mean(c))
                    es.append(ev.SE_FACTOR * ev.d_se(c))
        if xs:
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name=name, error_y=dict(type="data", array=es, visible=True),
                                     hovertemplate="%{x}: %{y:+.2f} Plätze<extra>" + name + "</extra>"))
    fig.add_hline(y=0, line_color="rgba(128,128,128,0.7)", line_width=1)
    fig.update_xaxes(title_text=title)
    fig.update_yaxes(title_text="Platzänderung (positiv = Gambit schlechter)")
    return _base(fig, height=380)

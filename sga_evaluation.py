"""Kennzahlen, Verdikte, Messreihen (vorgerechnet in data/gambit_grid.json) und das Live-Beispiel (ein Turnier-Paar ehrlich/Gambit).

Wörter wie „schlechter“ stehen nur, wo die Zählung der Zellen sie trägt: `d_se` ist der Standardfehler der Platzänderung über die Felder (gepaart, gleiche Felder),
„gesichert“ heißt hier: Mittel der Änderung mehr als zwei Standardfehler von null entfernt. Das ist eine Lesehilfe für 150 bis 300 Felder, kein Beweis."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import sga_algorithm as A
import sga_constants as C
from sga_scenario import make_field

GRID_PATH = Path(__file__).resolve().parent / "data" / "gambit_grid.json"
SE_FACTOR = 2.0   # „gesichert“: |Mittel der Platzänderung| > SE_FACTOR · Standardfehler


# --- Formatierung (deutsches Dezimalkomma) ---------------------------------------------------------------------------------------------------------

def de(value: float, digits: int = 2) -> str:
    return f"{round(value, digits) + 0.0:.{digits}f}".replace(".", ",")


def pct(value: float, digits: int = 1) -> str:
    return f"{round(100 * value, digits) + 0.0:.{digits}f}".replace(".", ",") + " %"


def signed(value: float, digits: int = 2) -> str:
    return ("+" if value > 0 else "") + de(value, digits)


# --- Live-Beispiel -----------------------------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    rounds: int = C.DEFAULT_ROUNDS
    spread: int = C.DEFAULT_SPREAD
    seat: int = C.DEFAULT_SEAT
    gambit_round: int = C.DEFAULT_GAMBIT_ROUND
    kind: str = C.DEFAULT_KIND
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class GameRow:
    round_no: int
    opp_honest: int          # Setzplatz des Gegners im ehrlichen Turnier
    elo_honest: float
    score_honest: float      # Punkte dieser Partie
    total_honest: float      # Punkte nach dieser Runde
    opp_gambit: int
    elo_gambit: float
    score_gambit: float
    total_gambit: float


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    honest: A.Tournament
    gambit: A.Tournament
    place_honest: float
    place_gambit: float
    points_honest: float
    points_gambit: float
    opp_honest: float        # mittlere Stärke der Gegner, alle gespielten Runden
    opp_gambit: float
    opp_after_honest: float  # … nur Runden nach der Gambit-Runde
    opp_after_gambit: float
    rows: tuple[GameRow, ...]


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values)


def analyse(settings: Settings) -> Analysis:
    """Ein Feld, zwei Turniere: ehrlich und mit Gambit. Dieselbe Rechnung wie je Feld der Messreihen (`field_cells`)."""
    s = settings
    ratings = make_field(s.n, s.spread, s.seed)
    honest = A.run_tournament(ratings, s.rounds, s.seed)
    gambit = A.run_tournament(ratings, s.rounds, s.seed, A.Gambit(s.seat, s.gambit_round, s.kind))
    place_h, pts_h = A.standing(honest.players, s.seat)
    place_g, pts_g = A.standing(gambit.players, s.seat)
    gh, gg = honest.players[s.seat].games, gambit.players[s.seat].games
    rows, tot_h, tot_g = [], 0.0, 0.0
    for a, b in zip(gh, gg):
        tot_h, tot_g = tot_h + a.score, tot_g + b.score
        rows.append(GameRow(a.round_no, a.opponent, ratings[a.opponent - 1], a.score, tot_h, b.opponent, ratings[b.opponent - 1], b.score, tot_g))
    played = min(honest.rounds_played, gambit.rounds_played)
    after = min(s.gambit_round, max(played - 1, 0))
    return Analysis(
        s, honest, gambit, place_h, place_g, pts_h, pts_g,
        _mean(A.opponent_ratings(honest, s.seat)), _mean(A.opponent_ratings(gambit, s.seat)),
        _mean(A.opponent_ratings(honest, s.seat, after)) if played > after else float("nan"),
        _mean(A.opponent_ratings(gambit, s.seat, after)) if played > after else float("nan"),
        tuple(rows),
    )


def verdict_example(a: Analysis) -> tuple[str, str]:
    """Verdikt des einen Beispiel-Felds (ein Feld ist ein Einzelfall, keine Regel)."""
    s = a.settings
    if a.honest.rounds_played < s.rounds or a.gambit.rounds_played < s.rounds:
        return "warning", ("Die Engine fand in diesem Feld keine gültige Paarung für alle Runden (Art. 1.9.3): Das Beispiel ist unvollständig. "
                           "Anderen Zufalls-Seed oder weniger Runden wählen.")
    diff = a.place_gambit - a.place_honest
    head = (f"In diesem einen Feld (Zufalls-Seed {s.seed}) endet Setzplatz {s.seat} ehrlich auf Platz {de(a.place_honest, 1)} ({de(a.points_honest, 1)} Punkte), "
            f"mit Gambit auf Platz {de(a.place_gambit, 1)} ({de(a.points_gambit, 1)} Punkte); die Gegner sind im Mittel {de(a.opp_honest, 0)} bzw. {de(a.opp_gambit, 0)} Elo stark. ")
    if diff < 0:
        return "success", head + f"Hier hat sich der Gambit gelohnt (**{de(-diff, 1)}** Plätze besser). Ein Feld sagt nichts über den Durchschnitt: siehe die Messreihe unten."
    if diff > 0:
        return "info", head + f"Hier hat er geschadet (**{de(diff, 1)}** Plätze schlechter). Ein Feld sagt nichts über den Durchschnitt: siehe die Messreihe unten."
    return "info", head + "Hier ändert er den Platz nicht. Ein Feld sagt nichts über den Durchschnitt: siehe die Messreihe unten."


# --- Messreihen: Zellen -----------------------------------------------------------------------------------------------------------------------------

def field_cells(n: int, rounds: int, spread: float, field_seed: int, seats, variants) -> dict:
    """Ein Feld: das ehrliche Turnier einmal, je (Setzplatz, Runde, Art) ein Gambit-Turnier. Ergebnis je Schlüssel:
    (Platz ehrlich, Platz Gambit, Punkte ehrlich, Punkte Gambit, Gegner-Elo ehrlich, Gegner-Elo Gambit, … nur nach der Gambit-Runde ehrlich, … Gambit)."""
    ratings = make_field(n, spread, field_seed)
    honest = A.run_tournament(ratings, rounds, field_seed)
    if honest.rounds_played < rounds:
        raise RuntimeError(f"keine gültige Paarung: n={n}, Runden={rounds}, Feld={field_seed}")
    out = {}
    for seat in seats:
        place_h, pts_h = A.standing(honest.players, seat)
        opp_h = _mean(A.opponent_ratings(honest, seat))
        for round_no, kind in variants:
            gambit = A.run_tournament(ratings, rounds, field_seed, A.Gambit(seat, round_no, kind))
            if gambit.rounds_played < rounds:
                raise RuntimeError(f"keine gültige Paarung mit Gambit: n={n}, Runden={rounds}, Feld={field_seed}, Platz={seat}")
            place_g, pts_g = A.standing(gambit.players, seat)
            out[(seat, round_no, kind)] = (
                place_h, place_g, pts_h, pts_g, opp_h, _mean(A.opponent_ratings(gambit, seat)),
                _mean(A.opponent_ratings(honest, seat, round_no)), _mean(A.opponent_ratings(gambit, seat, round_no)),
            )
    return out


def aggregate_cell(n: int, rounds: int, spread: float, seat: int, round_no: int, kind: str, rows: list[tuple]) -> dict:
    """Aggregiert die Felder einer Zelle (in der Reihenfolge der Feld-Zufalls-Seeds) zu den gespeicherten Kennzahlen."""
    f = len(rows)
    diffs = [r[1] - r[0] for r in rows]
    mean_d = sum(diffs) / f
    sd = math.sqrt(sum((d - mean_d) ** 2 for d in diffs) / (f - 1)) if f > 1 else 0.0
    ordered = sorted(diffs)
    median = ordered[f // 2] if f % 2 else 0.5 * (ordered[f // 2 - 1] + ordered[f // 2])
    hist = [0] * C.HIST_BINS
    for d in diffs:
        hist[min(max(int((d - C.HIST_LO) // C.HIST_STEP), 0), C.HIST_BINS - 1)] += 1
    col = lambda i: sum(r[i] for r in rows) / f  # noqa: E731
    return {
        "n": n, "rounds": rounds, "spread": spread, "seat": seat, "round": round_no, "kind": kind, "fields": f,
        "hp": col(0), "gp": col(1), "hpts": col(2), "gpts": col(3), "hopp": col(4), "gopp": col(5), "hopp_after": col(6), "gopp_after": col(7),
        "d_sd": sd, "d_median": median,
        "better": sum(1 for d in diffs if d < 0), "equal": sum(1 for d in diffs if d == 0), "worse": sum(1 for d in diffs if d > 0),
        "top1_h": sum(1 for r in rows if r[0] <= 1.0), "top1_g": sum(1 for r in rows if r[1] <= 1.0),
        "top3_h": sum(1 for r in rows if r[0] <= 3.0), "top3_g": sum(1 for r in rows if r[1] <= 3.0),
        # gepaarte Zählung (McNemar): Felder, in denen nur der Gambit bzw. nur das ehrliche Spiel den Platz erreicht
        "top1_gain": sum(1 for r in rows if r[1] <= 1.0 < r[0]), "top1_loss": sum(1 for r in rows if r[0] <= 1.0 < r[1]),
        "top3_gain": sum(1 for r in rows if r[1] <= 3.0 < r[0]), "top3_loss": sum(1 for r in rows if r[0] <= 3.0 < r[1]),
        "hist": hist,
    }


def config_cells(n: int, rounds: int, spread: float, seats, variants, field_seeds) -> list[dict]:
    """Alle Zellen einer Konfiguration (n, Runden, Streuung): eine Aggregation je (Setzplatz, Runde, Art) über `field_seeds`."""
    per_field = [field_cells(n, rounds, spread, fs, seats, variants) for fs in field_seeds]
    return aggregate_config(n, rounds, spread, seats, variants, per_field)


def aggregate_config(n, rounds, spread, seats, variants, per_field: list[dict]) -> list[dict]:
    return [aggregate_cell(n, rounds, spread, seat, r, kind, [pf[(seat, r, kind)] for pf in per_field]) for seat in seats for r, kind in variants]


def typical_field(per_field: list[dict], seeds: list[int], seat: int, round_no: int, kind: str) -> dict:
    """Das Feld, dessen Platzänderung dem Mittel aller Felder am nächsten liegt (bei Gleichstand der kleinere Feld-Zufalls-Seed): das Beispiel-Feld der App.
    Gewählt nach dem Mittel, nicht danach, wie das Feld aussieht; ein Beispiel am Rand der Verteilung würde einen Einzelfall als Regel zeigen."""
    diffs = [pf[(seat, round_no, kind)][1] - pf[(seat, round_no, kind)][0] for pf in per_field]
    mean = sum(diffs) / len(diffs)
    best = min(range(len(diffs)), key=lambda i: (abs(diffs[i] - mean), seeds[i]))
    cell = per_field[best][(seat, round_no, kind)]
    return {"seed": seeds[best], "seat": seat, "round": round_no, "kind": kind, "place_honest": cell[0], "place_gambit": cell[1], "mean_change": mean}


def field_seeds(count: int) -> list[int]:
    return list(range(C.GRID_SEED_BASE, C.GRID_SEED_BASE + count))


def grid_probe() -> dict:
    """Kleine feste Probe aus denselben Erzeugern wie die Messreihen; tests/test_grid.py vergleicht sie mit der gespeicherten Probe."""
    return {"cells": config_cells(16, 5, 100, (1, 4), ((1, C.KIND_LOSE), (2, C.KIND_DRAW)), field_seeds(3))}


# --- Messreihen: lesen ------------------------------------------------------------------------------------------------------------------------------

def load_grid():
    """Die vorgerechneten Messreihen; None, wenn die Datei fehlt."""
    if not GRID_PATH.exists():
        return None
    return json.loads(GRID_PATH.read_text(encoding="utf-8"))


def index_cells(grid: dict) -> dict:
    return {(c["n"], c["rounds"], c["spread"], c["seat"], c["round"], c["kind"]): c for c in grid["cells"]}


def d_mean(cell: dict) -> float:
    """Mittlere Platzänderung: Gambit minus ehrlich (positiv = schlechterer Platz)."""
    return cell["gp"] - cell["hp"]


def d_se(cell: dict) -> float:
    return cell["d_sd"] / math.sqrt(cell["fields"])


def classify(cell: dict) -> str:
    """„worse“, „better“ oder „open“ (Mittel weniger als SE_FACTOR Standardfehler von null)."""
    d, se = d_mean(cell), d_se(cell)
    if d > SE_FACTOR * se:
        return "worse"
    if d < -SE_FACTOR * se:
        return "better"
    return "open"


def win_change(cell: dict, k: int = 1) -> tuple[int, int]:
    """(Felder, in denen nur der Gambit Platz k oder besser erreicht; Felder, in denen nur das ehrliche Spiel ihn erreicht). Platz 1 heißt allein Erster (Platz 1,0):
    ein geteilter erster Platz hat den gemittelten Platz 1,5 und zählt nicht."""
    return cell[f"top{k}_gain"], cell[f"top{k}_loss"]


def win_class(cell: dict, k: int = 1) -> str:
    """„better“ (Gambit erreicht den Platz in gesichert mehr Feldern), „worse“ oder „open“: gepaarte Zählung, Unterschied mehr als SE_FACTOR · Wurzel(gain + loss)
    (Vorzeichentest-Näherung; gibt es keine abweichenden Felder, ist der Fall offen)."""
    gain, loss = win_change(cell, k)
    se = math.sqrt(gain + loss)
    if gain - loss > SE_FACTOR * se:
        return "better"
    if loss - gain > SE_FACTOR * se:
        return "worse"
    return "open"


def tally_win(cells: list[dict], k: int = 1) -> dict:
    kinds = [win_class(c, k) for c in cells]
    return {"cells": len(cells), "better": kinds.count("better"), "worse": kinds.count("worse"), "open": kinds.count("open")}


def verdict_win(cells: list[dict]) -> tuple[str, str]:
    """Verdikt zur Siegchance (alleiniger Turniersieg, Platz 1,0) und zu Platz 1 bis 3 in den Setzplätzen der Hauptreihe."""
    c0 = cells[0]
    t1, t3 = tally_win(cells, 1), tally_win(cells, 3)
    base = (f"Alleiniger Turniersieg (Platz 1,0), gepaart gezählt über {c0['fields']} Felder (Gambit „Runde {c0['round']}: der Spieler {C.KIND_SHORT[c0['kind']]}“): "
            f"in **{t1['better']}** von {t1['cells']} Setzplätzen gesichert häufiger, in {t1['worse']} gesichert seltener, in {t1['open']} offen (Setzplätze ohne Turniersieg in beiden Turnieren zählen als offen). "
            f"Platz 1 bis 3: in {t3['better']} gesichert häufiger, in {t3['worse']} gesichert seltener, in {t3['open']} offen. ")
    if t1["better"] or t3["better"]:
        return "info", base + "Der Gambit verschlechtert hier den mittleren Endplatz, kann aber die Chance auf die vorderen Plätze erhöhen: Mittel und Spitze sind verschiedene Fragen."
    return "warning", base + "Auch für die vorderen Plätze ist der Gambit in dieser Einstellung nicht gesichert besser."


def main_cells(grid: dict, round_no: int, kind: str) -> list[dict]:
    """Hauptmessreihe (MAIN) für eine Gambit-Runde und Art: eine Zelle je Setzplatz, nach Setzplatz."""
    idx = index_cells(grid)
    m = C.MAIN
    return [idx[(m["n"], m["rounds"], m["spread"], seat, round_no, kind)] for seat in C.MAIN_SEATS]


def sens_cells(grid: dict, axis: str) -> list[dict]:
    """Empfindlichkeitsreihe (Runde 1, Niederlage): axis „size“ (Feldgröße × Rundenzahl, Streuung 150) oder „spread“ (Streuung, 32 Spieler, 7 Runden)."""
    idx = index_cells(grid)
    out = []
    if axis == "size":
        for n in C.SENS_N:
            for rounds in C.SENS_ROUNDS:
                out += [idx[(n, rounds, C.MAIN["spread"], seat, 1, C.KIND_LOSE)] for seat in C.sens_seats(n)]
    else:
        for spread in C.SENS_SPREADS:
            out += [idx[(C.MAIN["n"], C.MAIN["rounds"], spread, seat, 1, C.KIND_LOSE)] for seat in C.sens_seats(C.MAIN["n"])]
    return out


def tally(cells: list[dict]) -> dict:
    """Zählung der Zellen nach `classify`; dazu kleinste und größte mittlere Platzänderung."""
    kinds = [classify(c) for c in cells]
    diffs = [d_mean(c) for c in cells]
    return {"cells": len(cells), "worse": kinds.count("worse"), "better": kinds.count("better"), "open": kinds.count("open"), "d_min": min(diffs), "d_max": max(diffs)}


# --- Verdikte der Messreihen (reine Funktionen auf Zellen) ----------------------------------------------------------------------------------

def verdict_main(cells: list[dict]) -> tuple[str, str]:
    """Verdikt der Hauptmessreihe: Zählung über alle Setzplätze der gewählten Gambit-Runde und Art."""
    t = tally(cells)
    c0 = cells[0]
    kind_txt = C.KIND_SHORT[c0["kind"]]
    base = (f"Im Feld mit {c0['n']} Spielern, {c0['rounds']} Runden und Elo-Streuung {c0['spread']} (je Zelle {c0['fields']} gleiche Felder, Mittel des Endplatzes) "
            f"liegt der Gambit „Runde {c0['round']}: der Spieler {kind_txt}“ in **{t['worse']} von {t['cells']}** Setzplätzen gesichert schlechter als ehrliches Spiel "
            f"(Platzänderung zwischen {signed(t['d_min'])} und {signed(t['d_max'])}). ")
    if t["better"] == 0:
        return "warning", base + (f"In keinem Setzplatz ist er gesichert besser; in {t['open']} von {t['cells']} lässt sich die Änderung nicht von null unterscheiden. "
                                  "Gemessen ist nur diese einfache Strategie unter diesen Annahmen.")
    return "info", base + f"In **{t['better']}** Setzplätzen ist er gesichert besser, in {t['open']} unentschieden."


def verdict_opponents(cells: list[dict]) -> tuple[str, str]:
    """Verdikt zur Gegnerstärke: schwächere Gegner (Elo) mit Gambit, in allen Runden und nach der Gambit-Runde."""
    all_diff = [c["gopp"] - c["hopp"] for c in cells]
    after_diff = [c["gopp_after"] - c["hopp_after"] for c in cells]
    weaker_all = sum(1 for d in all_diff if d < 0)
    weaker_after = sum(1 for d in after_diff if d < 0)
    m = len(cells)
    text = (f"Mit Gambit sind die Gegner über alle Runden in **{weaker_all} von {m}** Setzplätzen im Mittel schwächer (Änderung zwischen {signed(min(all_diff), 1)} und {signed(max(all_diff), 1)} Elo), "
            f"in den Runden nach der Gambit-Runde in {weaker_after} von {m} (zwischen {signed(min(after_diff), 1)} und {signed(max(after_diff), 1)} Elo).")
    return ("info" if weaker_after else "warning"), text


def verdict_sens(cells: list[dict], axis: str) -> tuple[str, str]:
    """Verdikt der Empfindlichkeitsreihe: Zählung über alle Zellen der Reihe."""
    t = tally(cells)
    what = "Feldgröße und Rundenzahl" if axis == "size" else "Elo-Streuung"
    base = (f"Über {what} (Runde 1, Niederlage; {t['cells']} Zellen aus Setzplatz, Größe und Rundenzahl bzw. Streuung) ist der Gambit in **{t['worse']}** Zellen gesichert schlechter "
            f"als ehrliches Spiel, in {t['better']} gesichert besser und in {t['open']} unentschieden; die Platzänderung liegt zwischen {signed(t['d_min'])} und {signed(t['d_max'])}.")
    return ("warning" if t["better"] == 0 else "info"), base

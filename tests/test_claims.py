"""Jede Zahl der README steht hier und wird aus den vorgerechneten Messreihen (data/gambit_grid.json) nachgeschlagen (DEMO-PLAYBOOK §4, §11a).

Die Tabellen und Kernzahlen der README entstehen aus `numbers(grid)` in der Rundung der App (`ev.de`, `ev.pct`, `ev.signed`); die Tests prüfen, dass jede Zeile und jede Kernzahl wörtlich in der README steht.
Die Messreihen selbst sind durch `test_grid.py` (Aufbau, Probe, Zählungen) und das Orakel (`test_oracle_swiss_gambit.py`) abgesichert. Jede Zahl nennt in der README ihre Bedingung
(Feldgröße, Rundenzahl, Streuung, Zahl der Felder, Gambit-Runde und -Art) direkt daneben."""

from pathlib import Path

import pytest

import sga_constants as C
import sga_evaluation as ev

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
README = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
WORD = {"worse": "schlechter", "better": "besser", "open": "offen"}
KIND_WORD = {C.KIND_LOSE: "Niederlage", C.KIND_DRAW: "Remis"}
WIN_WORD = {"better": "häufiger", "worse": "seltener", "open": "offen"}


@pytest.fixture(scope="module")
def grid():
    g = ev.load_grid()
    assert g is not None
    return g


def _change(c: dict) -> str:
    return f"{ev.signed(ev.d_mean(c))} ± {ev.de(ev.SE_FACTOR * ev.d_se(c))}"


def numbers(grid: dict) -> dict:
    """Alle Tabellen (Zeilenlisten) und Kernzahlen (Wörter) der README."""
    idx = ev.index_cells(grid)
    m = C.MAIN
    main = lambda seat, r=1, kind=C.KIND_LOSE: idx[(m["n"], m["rounds"], m["spread"], seat, r, kind)]  # noqa: E731
    out: dict = {}
    f = main(1)["fields"]
    out["fields_main"] = str(f)
    # Tabelle A: Hauptreihe, Runde 1, Niederlage
    out["table_main"] = [
        f"| {s} | {ev.de(main(s)['hp'])} | {ev.de(main(s)['gp'])} | {_change(main(s))} | {WORD[ev.classify(main(s))]} | {ev.de(main(s)['hpts'])} / {ev.de(main(s)['gpts'])} |"
        for s in C.MAIN_SEATS
    ]
    # Tabelle B: Zählung der Urteile über die Setzplätze je Gambit-Runde und Art
    rows, total = [], {"worse": 0, "better": 0, "open": 0}
    for r in C.MAIN_ROUNDS:
        for kind in C.KINDS:
            t = ev.tally(ev.main_cells(grid, r, kind))
            for k in total:
                total[k] += t[k]
            w = ev.tally_win(ev.main_cells(grid, r, kind), 1)
            rows.append(f"| {r} | {KIND_WORD[kind]} | {t['worse']} | {t['open']} | {t['better']} | {ev.signed(t['d_min'])} bis {ev.signed(t['d_max'])} | {w['better']} / {w['open']} / {w['worse']} |")
    out["table_tally"] = rows
    out["tally_total"] = {k: str(v) for k, v in total.items()}
    out["tally_cells"] = str(sum(total.values()))
    better = [f"Setzplatz {c['seat']}, Runde {r}, {KIND_WORD[kind]}" for r in C.MAIN_ROUNDS for kind in C.KINDS for c in ev.main_cells(grid, r, kind) if ev.classify(c) == "better"]
    out["better_list"] = "; ".join(better) if better else "keine"
    # Tabelle C: Gegnerstärke, Runde 1, Niederlage und Remis
    rows = []
    for kind in C.KINDS:
        for s in C.MAIN_SEATS:
            c = main(s, 1, kind)
            rows.append(f"| {KIND_WORD[kind]} | {s} | {ev.de(c['hopp'], 0)} / {ev.de(c['gopp'], 0)} | {ev.signed(c['gopp'] - c['hopp'], 0)} | {ev.de(c['hopp_after'], 0)} / {ev.de(c['gopp_after'], 0)} | {ev.signed(c['gopp_after'] - c['hopp_after'], 0)} |")
    out["table_opp"] = rows
    # Gegnerstärke: in wie vielen Setzplätzen sind die Gegner mit Gambit im Mittel schwächer (alle Runden / nur nach der Gambit-Runde), je Art, Runde 1
    opp = {}
    for kind in C.KINDS:
        cells = ev.main_cells(grid, 1, kind)
        opp[kind] = {"all": str(sum(1 for c in cells if c["gopp"] < c["hopp"])), "after": str(sum(1 for c in cells if c["gopp_after"] < c["hopp_after"])), "of": str(len(cells)),
                     "min_all": ev.signed(min(c["gopp"] - c["hopp"] for c in cells), 0), "max_all": ev.signed(max(c["gopp"] - c["hopp"] for c in cells), 0),
                     "min_change": ev.signed(min(ev.d_mean(c) for c in cells)), "max_change": ev.signed(max(ev.d_mean(c) for c in cells))}
    out["opp"] = opp
    pts = {}
    for kind in C.KINDS:
        cells = [c for r in C.MAIN_ROUNDS for c in ev.main_cells(grid, r, kind)]
        pts[kind] = f"{sum(1 for c in cells if c['gpts'] < c['hpts'])} von {len(cells)}"
    out["pts_lower"] = pts
    wt = {k: ev.tally_win(ev.main_cells(grid, 1, k), 1) for k in C.KINDS}
    out["win_tally"] = {k: f"{v['better']} häufiger, {v['worse']} seltener, {v['open']} offen" for k, v in wt.items()}
    # Verteilung Setzplatz 1, Runde 1, Niederlage
    c1 = main(1)
    out["seat1"] = {
        "median": ev.signed(c1["d_median"], 2), "mean": ev.signed(ev.d_mean(c1)), "sd": ev.de(c1["d_sd"]),
        "better": str(c1["better"]), "equal": str(c1["equal"]), "worse": str(c1["worse"]),
        "top1": f"{ev.pct(c1['top1_h'] / f)} / {ev.pct(c1['top1_g'] / f)}", "top3": f"{ev.pct(c1['top3_h'] / f)} / {ev.pct(c1['top3_g'] / f)}",
        "pts": f"{ev.de(c1['hpts'])} / {ev.de(c1['gpts'])}",
    }
    # Siegchance Setzplatz 1 und 2, Runde 1, beide Arten (gepaart gezählt)
    win = {}
    for kind in C.KINDS:
        for s in (1, 2):
            cc = main(s, 1, kind)
            win[(kind, s)] = f"{cc['top1_h']} → {cc['top1_g']} von {f} (nur Gambit {cc['top1_gain']}, nur ehrlich {cc['top1_loss']}; {WIN_WORD[ev.win_class(cc, 1)]})"
    out["win"] = {f"{k}_{s}": v for (k, s), v in win.items()}
    # Tabellen D: Empfindlichkeit, Änderung je Setzplatz-Art
    def sens_row(label, n, rounds, spread):
        cells = {c["seat"]: c for c in (idx[(n, rounds, spread, s, 1, C.KIND_LOSE)] for s in C.sens_seats(n))}
        mid = n // 2
        cols = [_change(cells[1]), _change(cells[4]), _change(cells[8]), _change(cells[mid]) if mid not in (1, 4, 8) else "(= Platz 8)"]
        return f"| {label} | {cells[1]['fields']} | " + " | ".join(cols) + " |"
    out["table_size"] = [sens_row(f"{n} Spieler, {r} Runden", n, r, m["spread"]) for n in C.SENS_N for r in C.SENS_ROUNDS]
    out["table_spread"] = [sens_row(f"σ = {sp}", m["n"], m["rounds"], sp) for sp in C.SENS_SPREADS]
    ts, tp = ev.tally(ev.sens_cells(grid, "size")), ev.tally(ev.sens_cells(grid, "spread"))
    out["tally_size"] = {k: str(v) for k, v in ts.items()} | {"range": f"{ev.signed(ts['d_min'])} bis {ev.signed(ts['d_max'])}"}
    out["tally_spread"] = {k: str(v) for k, v in tp.items()} | {"range": f"{ev.signed(tp['d_min'])} bis {ev.signed(tp['d_max'])}"}
    ex = grid["meta"]["example"]
    out["example"] = {"seed": str(ex["seed"]), "honest": ev.de(ex["place_honest"], 1), "gambit": ev.de(ex["place_gambit"], 1), "mean_change": ev.signed(ex["mean_change"])}
    return out


@pytest.mark.parametrize("table", ["table_main", "table_tally", "table_opp", "table_size", "table_spread"])
def test_every_table_row_of_the_readme_is_computed_from_the_grid(grid, table):
    rows = numbers(grid)[table]
    assert rows
    for row in rows:
        assert row in README, row


def test_the_key_numbers_of_the_readme_are_computed_from_the_grid(grid):
    n = numbers(grid)
    s1 = n["seat1"]
    for text in (
        f"{n['fields_main']} gleiche Felder",
        f"Median {s1['median']}", f"Mittel {s1['mean']}", f"Gambit besser in {s1['better']}, gleich in {s1['equal']}, schlechter in {s1['worse']}",
        f"Turniersieg {s1['top1']}", f"Platz 1 bis 3 {s1['top3']}", f"Punkte {s1['pts']}",
        f"niedriger in {n['pts_lower']['lose']} Zellen mit Niederlage", f"{n['pts_lower']['draw']} Zellen mit Remis",
        f"zwischen {n['opp']['lose']['min_change']} und {n['opp']['lose']['max_change']} Plätzen", f"Gesichert besser nur in: {n['better_list']}", f"in **{n['tally_total']['worse']} von {n['tally_cells']}** Zellen", f"{n['tally_total']['better']} gesichert besser", f"{n['tally_total']['open']} offen",
        f"Niederlage in Runde 1: Gegner im Mittel schwächer in {n['opp']['lose']['all']} von {n['opp']['lose']['of']} Setzplätzen (alle Runden), in {n['opp']['lose']['after']} von {n['opp']['lose']['of']} (nach der Gambit-Runde)",
        f"Remis in Runde 1: Gegner im Mittel schwächer in {n['opp']['draw']['all']} von {n['opp']['draw']['of']} Setzplätzen (alle Runden), in {n['opp']['draw']['after']} von {n['opp']['draw']['of']} (nach der Gambit-Runde)",
        f"Alleiniger Turniersieg Setzplatz 1, Runde 1: Niederlage {n['win']['lose_1']}; Remis {n['win']['draw_1']}", f"Setzplatz 2 mit Remis: {n['win']['draw_2']}",
        f"Niederlage in {n['win_tally']['lose']}; Remis in {n['win_tally']['draw']} (alleiniger Turniersieg, gepaart gezählt)",
        f"Seed {n['example']['seed']}", f"Platz {n['example']['honest']} ehrlich", f"Platz {n['example']['gambit']} mit Gambit",
        f"{n['tally_size']['worse']} von {n['tally_size']['cells']} Zellen (Feldgröße und Rundenzahl)", f"{n['tally_size']['range']} Plätze",
        f"{n['tally_spread']['worse']} von {n['tally_spread']['cells']} Zellen (Elo-Streuung)", f"{n['tally_spread']['range']} Plätze",
    ):
        assert text in README, text


def test_the_readme_example_is_the_default_example_of_the_app(grid):
    """Das Beispiel-Feld der App ist das Feld der Hauptreihe mit der Platzänderung nächst dem Mittel (Setzplatz 1, Runde 1, Niederlage); die App rechnet es live nach."""
    ex = grid["meta"]["example"]
    assert ex["seed"] == C.DEFAULT_SEED and (ex["seat"], ex["round"], ex["kind"]) == (C.DEFAULT_SEAT, C.DEFAULT_GAMBIT_ROUND, C.DEFAULT_KIND)
    a = ev.analyse(ev.Settings())
    assert (a.place_honest, a.place_gambit) == (ex["place_honest"], ex["place_gambit"])
    assert C.GRID_SEED_BASE <= ex["seed"] < C.GRID_SEED_BASE + C.GRID_FIELDS_MAIN


def test_the_main_series_reproduces_the_pre_measurement_ordering(grid):
    """Die Vormessung (Notiz M5, 300 Felder, Python-`random`) fand den Gambit von Setzplatz 1, 4, 8 und 16 in Runde 1 schlechter; die Messreihe dieser Demo
    (SplitMix64, gemeinsame Zufallszahlen) bestätigt die Richtung in jedem dieser vier Setzplätze (Änderung positiv) und nennt die eigenen Zahlen in der README."""
    cells = {c["seat"]: c for c in ev.main_cells(grid, 1, C.KIND_LOSE)}
    assert all(ev.d_mean(cells[s]) > 0 for s in (1, 4, 8, 16))


def test_the_readme_names_the_test_count_and_the_runtime_section():
    assert "## Tests" in README and "## Verifikation" in README and "## Ehrliche Grenzen" in README and "## Befunde und Korrekturen gegenüber dem Plan" in README
    assert "nicht im Volltext gelesen" in README


def test_top_three_and_points_statements_of_the_readme_are_computed_from_the_grid(grid):
    """README (Spitze und Punkte): Platz 1 bis 3 mit Remis in 2 / 1 / 2 von 6 Setzplätzen gesichert häufiger (Runde 1 / 2 / 3), bei Niederlage in Runde 1 in 5 von 6 gesichert seltener;
    Punktverlust bei Niederlage in Runde 1 um 0,12 bis 0,53 Punkte; 3 von 18 Zellen mit Remis ohne niedrigere Punkte."""
    better3 = [ev.tally_win(ev.main_cells(grid, r, C.KIND_DRAW), 3)["better"] for r in C.MAIN_ROUNDS]
    assert better3 == [2, 1, 2]
    assert ev.tally_win(ev.main_cells(grid, 1, C.KIND_LOSE), 3)["worse"] == 5
    c1 = ev.main_cells(grid, 1, C.KIND_DRAW)[0]
    assert (c1["top3_h"], c1["top3_g"]) == (138, 170) and ev.win_class(c1, 3) == "better"
    assert (ev.main_cells(grid, 1, C.KIND_LOSE)[0]["top3_h"], ev.main_cells(grid, 1, C.KIND_LOSE)[0]["top3_g"]) == (138, 75)
    loss = [c["hpts"] - c["gpts"] for c in ev.main_cells(grid, 1, C.KIND_LOSE)]
    assert (ev.de(min(loss)), ev.de(max(loss))) == ("0,12", "0,53")
    draw_cells = [c for r in C.MAIN_ROUNDS for c in ev.main_cells(grid, r, C.KIND_DRAW)]
    assert sum(1 for c in draw_cells if not c["gpts"] < c["hpts"]) == 3 and len(draw_cells) == 18
    for text in ("Platz 1 bis 3 mit Remis: in Runde 1 in 2 von 6 Setzplätzen gesichert häufiger (Setzplatz 1: 138 → 170 von 300 Feldern), in Runde 2 in 1 von 6, in Runde 3 in 2 von 6",
                 "bei Niederlage in Runde 1 in 5 von 6 gesichert seltener (Setzplatz 1: 138 → 75)", "im Mittel 0,12 bis 0,53 Punkte weniger", "Mit Remis sind die Punkte in 3 von 18 Zellen nicht niedriger"):
        assert text in README, text


def test_the_three_open_cells_of_the_spread_series_are_the_ones_the_readme_names(grid):
    open_cells = [(c["spread"], c["seat"]) for c in ev.sens_cells(grid, "spread") if ev.classify(c) == "open"]
    mid = C.MAIN["n"] // 2
    assert sorted(open_cells) == sorted([(200, mid), (300, 8), (300, mid)])
    assert "die drei offenen Zellen der Streuungsreihe liegen bei Streuung 200 (Feldmitte) und 300 (Setzplatz 8 und Feldmitte)" in README


def test_preset_and_sidebar_texts_do_not_overstate():
    assert "fast reiner Zufall" not in C.PRESET_HELP["Enges Feld (Streuung 50)"] and "hängt stärker vom Zufall ab" in C.PRESET_HELP["Enges Feld (Streuung 50)"]
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "ganzen Punkt" not in app and "in jeder Runde möglichst Spieler" in app and "in jeder Runde möglichst Spieler" in README


def test_the_readme_ends_with_the_footer_paragraph_and_has_no_scaffold_leftovers():
    assert "TODO" not in README and "Gerüst" not in README.replace("Gerüst-Aufgabe", "")

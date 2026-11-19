"""Die vorgerechneten Messreihen (data/gambit_grid.json): Aufbau, Zählungen und Übereinstimmung mit dem Erzeuger (Probe)."""

import pytest

import sga_constants as C
import sga_evaluation as ev


@pytest.fixture(scope="module")
def grid():
    g = ev.load_grid()
    assert g is not None, "data/gambit_grid.json fehlt: python tools/make_grid.py"
    return g


def _assert_close(a, b, path="probe"):
    """Verschachtelte Wörter und Listen: Zahlen mit relativer Toleranz (Summationsreihenfolge je Plattform, DEMO-PLAYBOOK §4), alles andere exakt."""
    if isinstance(a, dict):
        assert set(a) == set(b), path
        for k in a:
            _assert_close(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            _assert_close(x, y, f"{path}[{i}]")
    elif isinstance(a, float):
        assert a == pytest.approx(b, rel=1e-6, abs=1e-9), path
    else:
        assert a == b, path


def _expected_keys():
    m = C.MAIN
    keys = {(m["n"], m["rounds"], m["spread"], s, r, k) for s in C.MAIN_SEATS for r in C.MAIN_ROUNDS for k in C.KINDS}
    for n in C.SENS_N:
        for rounds in C.SENS_ROUNDS:
            if (n, rounds) != (m["n"], m["rounds"]):
                keys |= {(n, rounds, m["spread"], s, 1, C.KIND_LOSE) for s in C.sens_seats(n)}
    for spread in C.SENS_SPREADS:
        if spread != m["spread"]:
            keys |= {(m["n"], m["rounds"], spread, s, 1, C.KIND_LOSE) for s in C.sens_seats(m["n"])}
    return keys


def test_probe_still_matches_the_generator(grid):
    """Ändert sich Erzeuger, Rechnung oder Seed-Ableitung, passt die gespeicherte Probe nicht mehr: dann tools/make_grid.py neu laufen lassen."""
    _assert_close(ev.grid_probe(), grid["probe"])


def test_grid_has_every_cell_exactly_once(grid):
    keys = [(c["n"], c["rounds"], c["spread"], c["seat"], c["round"], c["kind"]) for c in grid["cells"]]
    assert len(keys) == len(set(keys)) == len(_expected_keys())
    assert set(keys) == _expected_keys()


def test_grid_field_counts_and_meta(grid):
    main = (C.MAIN["n"], C.MAIN["rounds"], C.MAIN["spread"])
    for c in grid["cells"]:
        assert c["fields"] == (C.GRID_FIELDS_MAIN if (c["n"], c["rounds"], c["spread"]) == main else C.GRID_FIELDS_SENS), c
    assert grid["meta"]["seed_base"] == C.GRID_SEED_BASE and grid["meta"]["fields_main"] == C.GRID_FIELDS_MAIN and grid["meta"]["fields_sens"] == C.GRID_FIELDS_SENS
    assert len(grid["meta"]["configs"]) == 1 + (len(C.SENS_N) * len(C.SENS_ROUNDS) - 1) + (len(C.SENS_SPREADS) - 1)


def test_every_cell_is_internally_consistent(grid):
    for c in grid["cells"]:
        f = c["fields"]
        assert c["better"] + c["equal"] + c["worse"] == f == sum(c["hist"]) and len(c["hist"]) == C.HIST_BINS
        assert 1.0 <= c["hp"] <= c["n"] and 1.0 <= c["gp"] <= c["n"] and 0.0 <= c["hpts"] <= c["rounds"] and 0.0 <= c["gpts"] <= c["rounds"]
        assert 0 <= c["top1_h"] <= c["top3_h"] <= f and 0 <= c["top1_g"] <= c["top3_g"] <= f
        assert c["top1_g"] - c["top1_h"] == c["top1_gain"] - c["top1_loss"] and c["top3_g"] - c["top3_h"] == c["top3_gain"] - c["top3_loss"]
        assert 0 <= c["top1_gain"] + c["top1_loss"] <= f and 0 <= c["top3_gain"] + c["top3_loss"] <= f
        assert c["d_sd"] >= 0.0 and 1500.0 < c["hopp"] < 2500.0 and 1500.0 < c["gopp"] < 2500.0
        # Mittel der Platzänderung liegt zwischen kleinster und größter besetzter Klasse der Verteilung
        used = [i for i, k in enumerate(c["hist"]) if k]
        lo, hi = C.HIST_LO + C.HIST_STEP * used[0], C.HIST_LO + C.HIST_STEP * (used[-1] + 1)
        assert lo <= c["gp"] - c["hp"] <= hi, c


def test_the_honest_values_do_not_depend_on_the_gambit_variant(grid):
    """Das ehrliche Turnier eines Feldes ist für alle Gambit-Varianten desselben (Feld, Setzplatz) dasselbe: gleiche Mittel."""
    by_key = {}
    for c in grid["cells"]:
        by_key.setdefault((c["n"], c["rounds"], c["spread"], c["seat"]), []).append(c)
    assert any(len(v) > 1 for v in by_key.values())
    for key, cells in by_key.items():
        first_fields = {c["fields"] for c in cells}
        assert len(first_fields) == 1, key
        for name in ("hp", "hpts", "hopp", "top1_h", "top3_h"):
            assert all(c[name] == pytest.approx(cells[0][name], rel=1e-12) for c in cells), (key, name)


def test_the_first_150_fields_are_shared_between_main_and_sensitivity_series():
    """Die Empfindlichkeitsreihen nutzen die ersten 150 der 300 Feld-Zufalls-Seeds der Hauptreihe (gleiche Felder, kein neuer Zufall)."""
    assert ev.field_seeds(C.GRID_FIELDS_SENS) == ev.field_seeds(C.GRID_FIELDS_MAIN)[:C.GRID_FIELDS_SENS]


def test_no_variant_is_dead(grid):
    """Nullspalten-Regel (DEMO-PLAYBOOK §0): jede Variante weicht von der Nachbarvariante ab. Die Arten Niederlage und Remis ergeben in jeder Zelle der Hauptreihe verschiedene
    Endpunkte und Endplätze; die drei Gambit-Runden ergeben je Setzplatz verschiedene Endplätze und verschiedene Gegner nach der Gambit-Runde."""
    idx = ev.index_cells(grid)
    m = C.MAIN
    for seat in C.MAIN_SEATS:
        for r in C.MAIN_ROUNDS:
            lose, draw = (idx[(m["n"], m["rounds"], m["spread"], seat, r, k)] for k in C.KINDS[:2])
            assert draw["gpts"] != lose["gpts"] and draw["gp"] != lose["gp"], (seat, r)
    for seat in C.MAIN_SEATS:
        assert len({round(idx[(m["n"], m["rounds"], m["spread"], seat, r, "lose")]["gp"], 6) for r in C.MAIN_ROUNDS}) == 3, seat
        assert len({round(idx[(m["n"], m["rounds"], m["spread"], seat, r, "lose")]["gopp_after"], 6) for r in C.MAIN_ROUNDS}) == 3, seat
    main = ev.main_cells(grid, 1, C.KIND_LOSE)
    assert any(c["better"] > 0 for c in main) and any(c["worse"] > 0 for c in main)          # beide Ausgänge kommen vor
    assert len({round(c["gp"] - c["hp"], 6) for c in grid["cells"]}) > 20


def test_lookup_helpers_return_the_series_in_order(grid):
    for r in C.MAIN_ROUNDS:
        for kind in C.KINDS:
            cells = ev.main_cells(grid, r, kind)
            assert [c["seat"] for c in cells] == list(C.MAIN_SEATS) and all(c["round"] == r and c["kind"] == kind for c in cells)
    size = ev.sens_cells(grid, "size")
    assert len(size) == sum(len(C.sens_seats(n)) for n in C.SENS_N for _ in C.SENS_ROUNDS)
    assert len(ev.sens_cells(grid, "spread")) == len(C.SENS_SPREADS) * len(C.sens_seats(C.MAIN["n"]))


def test_a_field_of_the_series_equals_the_live_example():
    """Ein Feld der Messreihe ist dasselbe Turnier-Paar wie das Live-Beispiel: Platz, Punkte und Gegnerstärke stimmen überein (Feld-Zufalls-Seed 1000, Setzplatz 8, Runde 2, Remis)."""
    cells = ev.field_cells(16, 5, 100, 1000, (8,), ((2, "draw"),))
    a = ev.analyse(ev.Settings(n=16, rounds=5, spread=100, seat=8, gambit_round=2, kind="draw", seed=1000))
    hp, gp, hpts, gpts, hopp, gopp, hafter, gafter = cells[(8, 2, "draw")]
    assert (hp, gp, hpts, gpts) == (a.place_honest, a.place_gambit, a.points_honest, a.points_gambit)
    assert (hopp, gopp, hafter, gafter) == pytest.approx((a.opp_honest, a.opp_gambit, a.opp_after_honest, a.opp_after_gambit))

"""Abbildungen: alle Achsen gesperrt (fixedrange), die Spuren haben die erwartete Zahl an Punkten und keine NaN-Werte."""

import math

import pytest

import sga_constants as C
import sga_evaluation as ev
import sga_visualization as V


@pytest.fixture(scope="module")
def grid():
    g = ev.load_grid()
    assert g is not None
    return g


def _locked(fig):
    axes = [v for k, v in fig.layout.to_plotly_json().items() if k.startswith(("xaxis", "yaxis"))]
    assert axes and all(a.get("fixedrange") is True for a in axes)


def _numbers(fig):
    return [v for trace in fig.data for key in ("x", "y") for v in (trace[key] or []) if isinstance(v, (int, float))]


def test_main_places_has_one_bar_pair_per_seat_and_marks_the_chosen_seat(grid):
    cells = ev.main_cells(grid, 1, C.KIND_LOSE)
    fig = V.build_main_places(cells, highlight_seat=8)
    _locked(fig)
    assert [len(t.x) for t in fig.data] == [len(C.MAIN_SEATS)] * 2
    assert list(fig.data[0].x) == [f"Platz {s}" + (" ★" if s == 8 else "") for s in C.MAIN_SEATS]
    assert not any(math.isnan(v) for v in _numbers(fig))
    assert [t.name for t in V.build_main_places(cells).data] == ["ehrlich", "Gambit"] and all("★" not in x for x in V.build_main_places(cells).data[0].x)


@pytest.mark.parametrize("after", [False, True])
def test_opponent_chart_uses_the_requested_columns(grid, after):
    cells = ev.main_cells(grid, 2, C.KIND_DRAW)
    fig = V.build_opponents(cells, after)
    _locked(fig)
    hk, gk = ("hopp_after", "gopp_after") if after else ("hopp", "gopp")
    assert list(fig.data[0].y) == [c[hk] for c in cells] and list(fig.data[1].y) == [c[gk] for c in cells]
    lo, hi = fig.layout.yaxis.range
    assert lo < min(fig.data[0].y) and hi > max(fig.data[1].y) and lo < min(fig.data[1].y) and hi > max(fig.data[0].y)


def test_histogram_bars_add_up_to_the_fields_and_are_coloured_by_sign(grid):
    for cell in ev.main_cells(grid, 1, C.KIND_LOSE):
        fig = V.build_difference_hist(cell)
        _locked(fig)
        assert sum(fig.data[0].y) == cell["fields"]
        labels, colors = list(fig.data[0].x), list(fig.data[0].marker.color)
        for label, color in zip(labels, colors):
            assert color == (C.COLOR_HONEST if int(label) < 0 else C.COLOR_NEUTRAL if int(label) == 0 else C.COLOR_GAMBIT)


@pytest.mark.parametrize("axis, x_count", [("size", 9), ("spread", len(C.SENS_SPREADS))])
def test_sensitivity_chart_has_one_line_per_seat_kind_with_error_bars(grid, axis, x_count):
    fig = V.build_sensitivity(ev.sens_cells(grid, axis), axis)
    _locked(fig)
    assert [t.name for t in fig.data][:3] == ["Setzplatz 1", "Setzplatz 4", "Setzplatz 8"]
    assert len(fig.data[0].x) == x_count and all(e >= 0 for e in fig.data[0].error_y.array)
    assert not any(math.isnan(v) for v in _numbers(fig))


def test_example_chart_has_both_tournaments_in_both_panels():
    a = ev.analyse(ev.Settings(n=16, rounds=5, spread=100, seat=4, gambit_round=2, kind=C.KIND_LOSE, seed=C.DEFAULT_SEED))
    fig = V.build_example(a)
    _locked(fig)
    assert len(fig.data) == 4 and all(len(t.x) == 5 for t in fig.data)
    assert list(fig.data[0].y)[-1] == a.points_honest and list(fig.data[1].y)[-1] == a.points_gambit

"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, fährt jeden Regler an seine Grenzen,
setzt jede Auswahl und prüft, dass kein Python-Fehler auftritt und die Abschnitte der Seite da sind."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import sga_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "▶"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at) -> str:
    return " ".join([m.value for m in at.markdown] + [i.value for i in at.info] + [w.value for w in at.warning] + [s.value for s in at.success] + [c.value for c in at.caption])


def test_app_loads_without_exception_and_shows_every_section():
    at = _fresh_app()
    assert not at.error
    subheaders = [s.value for s in at.subheader]
    for part in ("Experiment 1", "Experiment 2", "Experiment 3", "Experiment 4", "Wo die Annahmen enden"):
        assert any(part in s for s in subheaders), part
    labels = [e.label for e in at.expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels and any(label.startswith("So funktioniert") for label in labels)
    text = _texts(at)
    assert "Ein Beispiel-Feld" in text and "Kernfrage" in text and "In diesem einen Feld" in text and "gesichert schlechter" in text
    assert len(at.get("plotly_chart")) == 7                    # Beispiel, Hauptreihe, zwei Gegnerabbildungen (Reiter), Verteilung, zwei Empfindlichkeitsreihen


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert len(labels) == 5, labels
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


@pytest.mark.parametrize("edge", ["min", "max"])
def test_all_sliders_together_at_their_minima_and_maxima(edge):
    at = _fresh_app()
    for key in ("n_slider", "rounds_slider", "spread_slider"):
        s = at.sidebar.slider(key=key)
        s.set_value(int(s.min if edge == "min" else s.max))
    at.run(timeout=TIMEOUT)
    for key in ("seat_slider", "gambit_round_slider"):
        s = at.sidebar.slider(key=key)
        s.set_value(int(s.min if edge == "min" else s.max))
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    seat = at.sidebar.slider(key="seat_slider").value
    assert seat == (1 if edge == "min" else at.sidebar.slider(key="n_slider").value)


def test_the_seed_field_at_its_bounds_and_the_dice_button():
    for value in (0, C.SEED_MAX):
        at = _fresh_app()
        at.sidebar.number_input(key="seed_input").set_value(value).run(timeout=TIMEOUT)
        assert not at.exception, [str(e) for e in at.exception]
        assert f"Zufalls-Seed {value}" in _texts(at)


@pytest.mark.parametrize("kind", C.KINDS)
@pytest.mark.parametrize("gambit_round", range(C.GAMBIT_ROUND_MIN, C.GAMBIT_ROUND_MAX + 1))
def test_every_gambit_round_and_kind_drives_the_main_series_and_the_example(gambit_round, kind):
    at = _fresh_app()
    at.sidebar.slider(key="gambit_round_slider").set_value(gambit_round).run(timeout=TIMEOUT)
    at.sidebar.radio(key="kind_radio").set_value(kind).run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    text = _texts(at)
    assert f"Runde {gambit_round}: der Spieler {C.KIND_SHORT[kind]}" in text          # Verdikt der Hauptreihe
    assert any(f"Runde {gambit_round}, {C.KIND_SHORT[kind]}" in i.value for i in at.info)      # Verteilung (Experiment 2)
    table = at.dataframe[0].value
    assert ("absichtlich" in " ".join(table["Gambit: Ergebnis"]))


@pytest.mark.parametrize("seat", C.MAIN_SEATS)
def test_every_seat_of_the_histogram_selector_runs(seat):
    at = _fresh_app()
    at.selectbox(key="hist_seat").set_value(seat).run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert any(f"Setzplatz {seat}, Runde 1" in i.value for i in at.info)


def test_a_seat_outside_the_main_series_says_so_and_a_seat_inside_shows_the_cell():
    at = _fresh_app()
    at.sidebar.slider(key="seat_slider").set_value(5).run(timeout=TIMEOUT)
    assert not at.exception and "liegt nicht in der Messreihe" in _texts(at)
    at.sidebar.slider(key="seat_slider").set_value(8).run(timeout=TIMEOUT)
    assert "liegt nicht in der Messreihe" not in _texts(at) and any(m.label.startswith("Platz 8") for m in at.metric)


def test_missing_grid_file_is_reported_instead_of_a_traceback(monkeypatch, tmp_path):
    import sga_evaluation as ev
    monkeypatch.setattr(ev, "GRID_PATH", tmp_path / "fehlt.json")
    assert ev.load_grid() is None

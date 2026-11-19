"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; Permalink-Begrenzung."""

import sga_constants as C
import sga_evaluation as ev
import sga_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert C.N_MIN <= p["n"] <= C.N_MAX and (p["n"] - C.N_MIN) % C.N_STEP == 0, name
        assert C.ROUNDS_MIN <= p["rounds"] <= C.ROUNDS_MAX, name
        assert C.SPREAD_MIN <= p["spread"] <= C.SPREAD_MAX and (p["spread"] - C.SPREAD_MIN) % C.SPREAD_STEP == 0, name
        assert 1 <= p["seat"] <= p["n"], name                          # der Setzplatz passt in das Feld des Presets
        assert C.GAMBIT_ROUND_MIN <= p["gambit_round"] <= C.GAMBIT_ROUND_MAX and p["gambit_round"] < p["rounds"], name
        assert p["kind"] in C.KINDS and 0 <= p["seed"] <= C.SEED_MAX, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Setzplatz 1 verliert Runde 1 (Standard)"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_the_default_matches_the_main_measurement_series():
    """Die Hauptmessreihe gilt für 32 Spieler, 7 Runden, Streuung 150: genau die Voreinstellung."""
    d = ev.Settings()
    assert (d.n, d.rounds, d.spread) == (C.MAIN["n"], C.MAIN["rounds"], C.MAIN["spread"])


def test_the_example_seed_is_one_of_the_grid_fields():
    """Das Beispiel-Feld der Voreinstellung ist ein Feld der Hauptreihe (nicht ausgesucht nach Aussehen: tests/test_claims.py prüft, dass es das Feld mit der Platzänderung nächst dem Mittel ist)."""
    assert C.GRID_SEED_BASE <= C.DEFAULT_SEED < C.GRID_SEED_BASE + C.GRID_FIELDS_MAIN


def test_main_seats_are_inside_the_main_field_and_sensitivity_seats_inside_every_field():
    assert max(C.MAIN_SEATS) <= C.MAIN["n"] and C.MAIN_ROUNDS == tuple(range(C.GAMBIT_ROUND_MIN, C.GAMBIT_ROUND_MAX + 1))
    for n in C.SENS_N:
        assert all(1 <= s <= n for s in C.sens_seats(n)) and C.sens_seats(n) == tuple(sorted(set(C.sens_seats(n))))
    assert set(C.sens_seats(C.MAIN["n"])) <= set(C.MAIN_SEATS)      # die Zellen mit 32 Spielern und 7 Runden kommen aus der Hauptreihe
    assert C.MAIN["spread"] in C.SENS_SPREADS and C.MAIN["n"] in C.SENS_N and C.MAIN["rounds"] in C.SENS_ROUNDS
    assert C.GRID_FIELDS_SENS <= C.GRID_FIELDS_MAIN

"""Verdikte an von Hand gesetzten Zellen (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import math

import sga_constants as C
import sga_evaluation as ev


def cell(seat=1, hp=4.0, gp=6.0, sd=4.0, fields=100, hopp=2050.0, gopp=2000.0, hopp_after=2060.0, gopp_after=2010.0, **kw):
    base = {"n": 32, "rounds": 7, "spread": 150, "seat": seat, "round": 1, "kind": "lose", "fields": fields, "hp": hp, "gp": gp, "hpts": 5.0, "gpts": 4.5,
            "hopp": hopp, "gopp": gopp, "hopp_after": hopp_after, "gopp_after": gopp_after, "d_sd": sd, "d_median": 1.5, "better": 20, "equal": 20, "worse": 60,
            "top1_h": 10, "top1_g": 5, "top3_h": 30, "top3_g": 20, "top1_gain": 0, "top1_loss": 5, "top3_gain": 2, "top3_loss": 12, "hist": [0] * C.HIST_BINS}
    return base | kw


def test_classify_threshold_is_two_standard_errors_inclusive_of_the_boundary_as_open():
    se = 4.0 / math.sqrt(100)                                           # 0,4
    assert ev.d_se(cell()) == 0.4 and ev.d_mean(cell()) == 2.0
    assert ev.classify(cell(hp=4.0, gp=4.0 + 2 * se + 0.01)) == "worse"
    assert ev.classify(cell(hp=4.0, gp=4.0 + 2 * se)) == "open"          # genau 2 SE: nicht gesichert
    assert ev.classify(cell(hp=4.0, gp=4.0 - 2 * se - 0.01)) == "better"
    assert ev.classify(cell(hp=4.0, gp=4.0)) == "open"


def test_tally_counts_and_range():
    cells = [cell(gp=6.0), cell(gp=4.0), cell(gp=1.0), cell(gp=4.2)]    # +2,0 gesichert schlechter; 0 offen; -3,0 gesichert besser; +0,2 offen
    t = ev.tally(cells)
    assert (t["cells"], t["worse"], t["better"], t["open"]) == (4, 1, 1, 2)
    assert t["d_min"] == -3.0 and t["d_max"] == 2.0


def test_verdict_main_names_counts_setting_and_range_without_a_better_cell():
    cells = [cell(seat=1, gp=6.0), cell(seat=2, gp=5.0), cell(seat=4, gp=4.1)]    # +2,0, +1,0 (beide gesichert), +0,1 (offen)
    kind, text = ev.verdict_main(cells)
    assert kind == "warning"
    assert "**2 von 3** Setzplätzen gesichert schlechter" in text
    assert "32 Spielern, 7 Runden und Elo-Streuung 150" in text and "100 gleiche Felder" in text and "Runde 1: der Spieler verliert" in text
    assert "zwischen +0,10 und +2,00" in text
    assert "In keinem Setzplatz ist er gesichert besser; in 1 von 3 lässt sich die Änderung nicht von null unterscheiden." in text


def test_verdict_main_with_a_better_cell_is_not_a_warning_and_says_so():
    cells = [cell(seat=1, gp=6.0, kind="draw"), cell(seat=2, gp=1.0, kind="draw")]
    kind, text = ev.verdict_main(cells)
    assert kind == "info" and "In **1** Setzplätzen ist er gesichert besser, in 0 unentschieden." in text and "spielt Remis" in text


def test_verdict_opponents_counts_weaker_opponents_in_all_rounds_and_after_the_gambit_round():
    cells = [cell(gopp=2000.0, hopp=2050.0, gopp_after=2070.0, hopp_after=2060.0),     # -50 alle, +10 danach
             cell(gopp=2060.0, hopp=2050.0, gopp_after=2000.0, hopp_after=2060.0)]     # +10 alle, -60 danach
    kind, text = ev.verdict_opponents(cells)
    assert kind == "info"
    assert "in **1 von 2** Setzplätzen im Mittel schwächer (Änderung zwischen -50,0 und +10,0 Elo)" in text
    assert "in den Runden nach der Gambit-Runde in 1 von 2 (zwischen -60,0 und +10,0 Elo)" in text


def test_verdict_opponents_warns_when_no_cell_has_weaker_opponents_after_the_gambit_round():
    kind, _ = ev.verdict_opponents([cell(gopp_after=2070.0, hopp_after=2060.0)])
    assert kind == "warning"


def test_verdict_sens_names_axis_counts_and_range():
    cells = [cell(gp=6.0), cell(gp=4.0), cell(gp=1.0)]
    kind, text = ev.verdict_sens(cells, "size")
    assert kind == "info" and "Feldgröße und Rundenzahl" in text and "3 Zellen" in text and "in **1** Zellen gesichert schlechter" in text
    assert "in 1 gesichert besser und in 1 unentschieden" in text and "zwischen -3,00 und +2,00" in text
    kind, text = ev.verdict_sens([cell(gp=6.0)], "spread")
    assert kind == "warning" and "Elo-Streuung" in text


def _analysis_stub(place_h, place_g, rounds_played=7):
    class T:
        pass
    h, g = T(), T()
    h.rounds_played = g.rounds_played = rounds_played
    return ev.Analysis(ev.Settings(seat=4, seed=77), h, g, place_h, place_g, 5.0, 4.0, 2050.0, 2010.0, 2060.0, 2020.0, ())


def test_verdict_example_cases():
    kind, text = ev.verdict_example(_analysis_stub(3.0, 5.5))
    assert kind == "info" and "Zufalls-Seed 77" in text and "endet Setzplatz 4 ehrlich auf Platz 3,0 (5,0 Punkte)" in text and "mit Gambit auf Platz 5,5 (4,0 Punkte)" in text
    assert "2050 bzw. 2010 Elo" in text and "geschadet (**2,5** Plätze schlechter)" in text
    kind, text = ev.verdict_example(_analysis_stub(5.5, 3.0))
    assert kind == "success" and "gelohnt (**2,5** Plätze besser)" in text
    kind, text = ev.verdict_example(_analysis_stub(3.0, 3.0))
    assert kind == "info" and "ändert er den Platz nicht" in text
    kind, text = ev.verdict_example(_analysis_stub(3.0, 3.0, rounds_played=5))
    assert kind == "warning" and "keine gültige Paarung" in text


def test_formatting_helpers():
    assert ev.de(1.005, 2) in ("1,00", "1,01") and ev.de(-0.0001, 2) == "0,00"
    assert ev.pct(0.1234) == "12,3 %" and ev.signed(2.0) == "+2,00" and ev.signed(-2.0) == "-2,00" and ev.signed(0.0) == "0,00"


def test_win_class_is_a_paired_count_with_a_two_se_threshold():
    assert ev.win_change(cell(top1_gain=3, top1_loss=9)) == (3, 9)
    assert ev.win_class(cell(top1_gain=0, top1_loss=5)) == "worse"        # Unterschied 5 > 2 * Wurzel(5) = 4,47
    assert ev.win_class(cell(top1_gain=0, top1_loss=4)) == "open"         # 4 = 2 * Wurzel(4): genau auf der Schwelle, nicht gesichert
    assert ev.win_class(cell(top1_gain=9, top1_loss=2)) == "better"       # 7 > 2 * Wurzel(11) = 6,63
    assert ev.win_class(cell(top1_gain=0, top1_loss=0)) == "open"         # kein abweichendes Feld: offen, keine Division
    assert ev.win_class(cell(top3_gain=12, top3_loss=1), 3) == "better" and ev.win_class(cell(top3_gain=2, top3_loss=12), 3) == "worse"


def test_verdict_win_names_counts_and_distinguishes_mean_from_peak():
    cells = [cell(seat=1, top1_gain=0, top1_loss=5), cell(seat=2, top1_gain=0, top1_loss=0, top3_gain=0, top3_loss=0)]
    kind, text = ev.verdict_win(cells)
    assert kind == "warning" and "in **0** von 2 Setzplätzen gesichert häufiger, in 1 gesichert seltener, in 1 offen" in text and "über 100 Felder" in text
    assert "Platz 1 bis 3: in 0 gesichert häufiger, in 1 gesichert seltener, in 1 offen" in text and "in dieser Einstellung nicht gesichert besser" in text
    kind, text = ev.verdict_win([cell(top1_gain=9, top1_loss=2), cell(seat=2, top1_gain=0, top1_loss=0)])
    assert kind == "info" and "in **1** von 2 Setzplätzen gesichert häufiger" in text and "Mittel und Spitze sind verschiedene Fragen" in text

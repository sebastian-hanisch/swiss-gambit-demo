"""Randfälle (DEMO-PLAYBOOK §12): kleinste Felder, gleiche Stärken, Ränder der Regler, Gambit auf dem letzten Setzplatz."""

import math

import sga_algorithm as A
import sga_constants as C
import sga_evaluation as ev
import sga_scenario as S


def test_four_players_one_round():
    """n = 4, T = 1: Setzplatz 1 gegen 3 und 2 gegen 4; ein Gambit in der einzigen Runde ist erlaubt."""
    t = A.run_tournament((2060.0, 2020.0, 1980.0, 1940.0), 1, 0, A.Gambit(1, 1))
    assert t.players[1].score == 0.0 and t.players[3].score == 1.0 and t.rounds_played == 1


def test_equal_players_win_half_the_games():
    ratings = S.make_field(16, 0.0, 1)
    assert S.expected_score(ratings[0], ratings[1]) == 0.5
    scores = [A.standing(A.run_tournament(ratings, 5, seed).players, 1)[1] for seed in range(60)]
    assert 0.35 < sum(scores) / len(scores) / 5 < 0.65               # grobe Plausibilität: Mittel etwa 0,5 der Punkte


def test_gambit_of_the_last_seat_and_of_the_first_seat_in_the_first_and_last_gambit_round():
    for seat in (1, 16):
        for gr in (1, 3):
            t = A.run_tournament(S.make_field(16, 150.0, 4), 4, 4, A.Gambit(seat, gr, C.KIND_LOSE))
            assert t.players[seat].games[gr - 1].score == 0.0 and A.check_tournament(t) == []


def test_slider_extremes_of_the_bounds_run_through():
    """Ränder: kleinstes Feld mit den meisten Runden, größtes Feld mit den wenigsten."""
    for n, rounds in ((C.N_MIN, C.ROUNDS_MAX), (C.N_MAX, C.ROUNDS_MIN)):
        a = ev.analyse(ev.Settings(n=n, rounds=rounds, spread=C.SPREAD_MIN, seat=n, gambit_round=C.GAMBIT_ROUND_MAX, kind=C.KIND_DRAW, seed=C.SEED_MAX))
        assert a.honest.rounds_played == rounds and a.gambit.rounds_played == rounds
        assert not math.isnan(a.opp_after_honest) and not math.isnan(a.opp_after_gambit)


def test_rounds_never_exceed_what_a_small_field_can_play():
    assert C.ROUNDS_MAX <= C.N_MIN - 1 and C.ROUNDS_MIN > C.GAMBIT_ROUND_MAX and C.N_MAX < 64 and C.N_MIN % 2 == 0 and C.N_STEP == 2


def test_aggregate_cell_with_a_single_field_and_with_ties_everywhere():
    """Ein Feld: Standardabweichung 0 statt Division durch null; gleicher Platz: Median 0, das Feld zählt als „gleich“."""
    row = (3.0, 3.0, 2.0, 2.0, 2000.0, 2000.0, 2000.0, 2000.0)
    c = ev.aggregate_cell(16, 5, 100, 1, 1, "lose", [row])
    assert c["d_sd"] == 0.0 and c["equal"] == 1 and c["d_median"] == 0.0 and sum(c["hist"]) == 1
    assert ev.classify(c) == "open"

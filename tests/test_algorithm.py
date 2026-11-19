"""Kern gegen Handrechnung auf Mini-Instanzen (DEMO-PLAYBOOK §1b): Ergebnisregel, Turnier, Gambit, Prüfer."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

import sga_algorithm as A
import sga_constants as C
import sga_scenario as S
from ss_model import Pairing

ROOT = Path(__file__).resolve().parent.parent
# Stärken mit so großen Abständen (mindestens 2000 Elo), dass die Elo-Erwartung 0,99999 ist: der Stärkere gewinnt in jedem der geprüften Felder.
DOMINANT = (8000.0, 6000.0, 4000.0, 2000.0)


def test_decide_game_forces_the_gambit_player_as_white_and_as_black():
    ratings = DOMINANT
    assert A.decide_game(Pairing(1, 3), 1, ratings, 0, A.Gambit(1, 1, C.KIND_LOSE)) is False   # Weiß = Gambit-Spieler verliert
    assert A.decide_game(Pairing(3, 1), 1, ratings, 0, A.Gambit(1, 1, C.KIND_LOSE)) is True    # Schwarz = Gambit-Spieler verliert
    assert A.decide_game(Pairing(1, 3), 1, ratings, 0, A.Gambit(1, 1, C.KIND_DRAW)) is None
    assert A.decide_game(Pairing(3, 1), 1, ratings, 0, A.Gambit(3, 1, C.KIND_DRAW)) is None


def test_decide_game_outside_the_gambit_round_or_without_the_gambit_player_follows_the_ratings():
    for seed in range(10):
        assert A.decide_game(Pairing(1, 3), 2, DOMINANT, seed, A.Gambit(1, 1, C.KIND_LOSE)) is True     # andere Runde: der Stärkere (Weiß) gewinnt
        assert A.decide_game(Pairing(4, 2), 1, DOMINANT, seed, A.Gambit(1, 1, C.KIND_LOSE)) is False    # Gambit-Spieler nicht beteiligt: Schwarz (Setzplatz 2) gewinnt
        assert A.decide_game(Pairing(3, 1), 1, DOMINANT, seed, None) is False                          # ohne Gambit: Schwarz (Setzplatz 1) gewinnt


def test_honest_tournament_by_hand():
    """Handrechnung: Runde 1: 1 schlägt 3, 2 schlägt 4; Runde 2: Sieger 1 gegen 2 (1 gewinnt), Verlierer 3 gegen 4 (3 gewinnt). Punkte 2, 1, 1, 0."""
    for seed in range(5):
        t = A.run_tournament(DOMINANT, 2, seed)
        assert [t.players[s].score for s in (1, 2, 3, 4)] == [2.0, 1.0, 1.0, 0.0]
        assert A.standing(t.players, 1) == (1.0, 2.0)
        assert A.standing(t.players, 2) == (2.5, 1.0)                    # Gleichstand mit Spieler 3: Plätze 2 und 3, gemittelt 2,5
        assert A.standing(t.players, 4) == (4.0, 0.0)
        assert t.rounds_played == 2 and A.check_tournament(t) == []


def test_gambit_in_round_one_by_hand():
    """Setzplatz 1 verliert Runde 1: 3 schlägt 1, 2 schlägt 4; Runde 2: Sieger 2 gegen 3 (2 gewinnt), Verlierer 1 gegen 4 (1 gewinnt). Punkte 1, 2, 1, 0."""
    for seed in range(5):
        t = A.run_tournament(DOMINANT, 2, seed, A.Gambit(1, 1, C.KIND_LOSE))
        assert [t.players[s].score for s in (1, 2, 3, 4)] == [1.0, 2.0, 1.0, 0.0]
        assert A.standing(t.players, 1) == (2.5, 1.0)
        assert A.check_tournament(t) == []


def test_gambit_in_round_two_by_hand():
    """Setzplatz 2 verliert Runde 2: Runde 1 wie ehrlich (1 schlägt 3, 2 schlägt 4), Runde 2: 1 schlägt 2, 3 schlägt 4. Punkte 2, 1, 1, 0."""
    t = A.run_tournament(DOMINANT, 2, 0, A.Gambit(2, 2, C.KIND_LOSE))
    assert [t.players[s].score for s in (1, 2, 3, 4)] == [2.0, 1.0, 1.0, 0.0]
    assert [g.score for g in t.players[2].games] == [1.0, 0.0]


def test_draw_gives_half_a_point_to_both_players_of_the_game():
    t = A.run_tournament(DOMINANT, 2, 0, A.Gambit(1, 1, C.KIND_DRAW))
    first = t.players[1].games[0]
    assert first.score == 0.5 and t.players[first.opponent].games[0].score == 0.5


def test_rounds_before_the_gambit_round_are_identical_and_the_forced_result_stands():
    ratings = S.make_field(16, 150.0, 11)
    honest = A.run_tournament(ratings, 5, 11)
    gambit = A.run_tournament(ratings, 5, 11, A.Gambit(3, 3, C.KIND_LOSE))
    assert honest.pairings[:2] == gambit.pairings[:2]
    for seat in range(1, 17):
        assert honest.players[seat].games[:2] == gambit.players[seat].games[:2]
    g3 = gambit.players[3].games[2]
    assert g3.score == 0.0 and gambit.players[g3.opponent].games[2].score == 1.0


def test_standing_with_ties_by_hand():
    from ss_model import Player
    players = {1: Player(1, 3.0), 2: Player(2, 2.0), 3: Player(3, 2.0), 4: Player(4, 2.0), 5: Player(5, 0.0)}
    assert A.standing(players, 1) == (1.0, 3.0)
    assert A.standing(players, 3) == (3.0, 2.0)          # 1 + 1 (besser) + 2/2 (zwei weitere mit 2 Punkten)
    assert A.standing(players, 5) == (5.0, 0.0)


def test_opponent_ratings_by_hand():
    t = A.run_tournament(DOMINANT, 2, 0)
    assert A.opponent_ratings(t, 1) == [4000.0, 6000.0]                  # 3, dann 2
    assert A.opponent_ratings(t, 1, after_round=1) == [6000.0]
    assert A.opponent_ratings(t, 4, after_round=2) == []


def test_check_tournament_detects_a_broken_tournament():
    from dataclasses import replace

    from ss_model import GameRecord, Player
    t = A.run_tournament(DOMINANT, 2, 0)
    assert A.check_tournament(t) == []
    broken = dict(t.players)
    p = broken[1]
    games = (GameRecord(1, 3, "w", 1.0, False), GameRecord(2, 3, "b", 1.0, False))      # zweimal derselbe Gegner, Gegenpartie passt nicht
    broken[1] = Player(1, 2.0, games, p.float_history)
    problems = A.check_tournament(replace(t, players=broken))
    assert any("zweimal" in x for x in problems) and any("Gegenpartie" in x for x in problems)
    wrong_score = dict(t.players)
    wrong_score[4] = Player(4, 5.0, t.players[4].games, t.players[4].float_history)
    assert any("Punktestand" in x for x in A.check_tournament(replace(t, players=wrong_score)))


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        A.run_tournament((2000.0, 2000.0, 2000.0), 1, 0)                   # ungerade
    for bad in (A.Gambit(0, 1), A.Gambit(5, 1), A.Gambit(1, 0), A.Gambit(1, 3), A.Gambit(1, 1, "winning")):
        with pytest.raises(ValueError):
            A.run_tournament(DOMINANT, 2, 0, bad)


def test_every_random_field_gives_a_valid_tournament():
    for seed in range(12):
        ratings = S.make_field(16, 150.0, seed)
        for gambit in (None, A.Gambit(1, 1), A.Gambit(8, 2, C.KIND_DRAW), A.Gambit(16, 3)):
            t = A.run_tournament(ratings, 6, seed, gambit)
            assert t.rounds_played == 6 and A.check_tournament(t) == [], (seed, gambit)


def test_same_inputs_give_the_same_result_in_other_processes():
    """Gleiche Eingabe, gleiches Ergebnis, auch mit anderem PYTHONHASHSEED (nie über set-Reihenfolgen iterieren, DEMO-PLAYBOOK §1d)."""
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import sga_algorithm as A, sga_scenario as S; "
            "t = A.run_tournament(S.make_field(16, 150.0, 5), 5, 5, A.Gambit(2, 1)); "
            "print(repr(sorted((s, p.score, tuple(g.opponent for g in p.games)) for s, p in t.players.items())))")
    outs = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        outs.append(subprocess.run([sys.executable, "-c", code, str(ROOT)], capture_output=True, text=True, env=env, check=True).stdout)
    assert outs[0] == outs[1] and outs[0].strip()

"""Szenario: Felder und Zufallszahlen der Partien."""

import statistics

import pytest

import sga_scenario as S


def test_expected_score_by_hand():
    assert S.expected_score(2000.0, 2000.0) == 0.5
    assert S.expected_score(2400.0, 2000.0) == pytest.approx(10 / 11)        # 400 Elo Abstand: 1 / (1 + 10^-1)
    assert S.expected_score(2000.0, 2400.0) == pytest.approx(1 / 11)
    assert S.expected_score(2100.0, 2000.0) + S.expected_score(2000.0, 2100.0) == pytest.approx(1.0)


def test_field_is_sorted_descending_deterministic_and_has_n_players():
    f = S.make_field(16, 150.0, 7)
    assert len(f) == 16 and list(f) == sorted(f, reverse=True)
    assert f == S.make_field(16, 150.0, 7)
    assert f != S.make_field(16, 150.0, 8)


def test_the_spread_scales_the_same_standard_normal_values():
    """Dieselben z für jede Streuung: (Stärke - 2000) / Streuung ist unabhängig von der Streuung."""
    a, b = S.make_field(12, 50.0, 3), S.make_field(12, 200.0, 3)
    assert [(x - 2000.0) / 50.0 for x in a] == pytest.approx([(x - 2000.0) / 200.0 for x in b])


def test_zero_spread_gives_equal_players():
    assert set(S.make_field(8, 0.0, 1)) == {2000.0}


def test_field_statistics_over_many_seeds():
    """Mittel der Stärken nahe 2000, Standardabweichung nahe der Streuung (400 Felder à 32 Spieler, Spielraum weit über dem Zufallsfehler)."""
    values = [x for seed in range(400) for x in S.make_field(32, 150.0, seed)]
    assert statistics.fmean(values) == pytest.approx(2000.0, abs=3.0)
    assert statistics.pstdev(values) == pytest.approx(150.0, rel=0.03)


def test_game_uniform_is_symmetric_in_the_pair_and_depends_on_every_key():
    u = S.game_uniform(5, 2, 3, 9)
    assert u == S.game_uniform(5, 2, 9, 3)
    assert 0.0 <= u < 1.0
    assert len({u, S.game_uniform(6, 2, 3, 9), S.game_uniform(5, 3, 3, 9), S.game_uniform(5, 2, 3, 10), S.game_uniform(5, 2, 4, 9)}) == 5


def test_game_uniform_looks_uniform():
    values = [S.game_uniform(seed, 1, 2, 5) for seed in range(4000)]
    assert statistics.fmean(values) == pytest.approx(0.5, abs=0.02)
    assert sum(1 for v in values if v < 0.25) / 4000 == pytest.approx(0.25, abs=0.03)


def test_low_seat_wins_follows_the_elo_expectation_in_both_argument_orders():
    ratings = (2400.0, 2000.0)                                                  # Erwartung des Stärkeren 10/11
    wins = sum(S.low_seat_wins(ratings, seed, 1, 1, 2) for seed in range(4000)) / 4000
    assert wins == pytest.approx(10 / 11, abs=0.02)
    assert all(S.low_seat_wins(ratings, seed, 1, 1, 2) == S.low_seat_wins(ratings, seed, 1, 2, 1) for seed in range(50))

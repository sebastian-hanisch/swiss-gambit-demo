"""Orakel-Test swiss-gambit-demo / swiss_gambit: Erwartungswert des Endplatzes für ein winziges Turnier (4 Spieler, 2 Runden) durch vollständiges Aufzählen
aller Ergebnisse mit ihren Wahrscheinlichkeiten, gegen die Simulation mit der Engine der Demo.

Anderer Rechenweg als die Demo: Das Orakel kennt keine Engine und keine Zufallszahlen. Es leitet die Paarungen selbst aus der Regel ab (Runde 1: obere gegen untere Hälfte,
also 1-3 und 2-4; Runde 2: die beiden Sieger gegeneinander und die beiden Verlierer gegeneinander, weil sich niemand aus verschiedenen Partien schon getroffen hat) und rechnet
die Platzverteilung exakt mit `fractions`. Die Simulation mit festen Feld-Zufalls-Seeds muss den exakten Erwartungswert innerhalb von 4,5 Standardfehlern treffen.
Das Orakel ist an einer Handrechnung geprüft (`test_the_oracle_by_hand`). Gambit-Art „Remis“ ist nicht aufgezählt: Die Paarung der zweiten Runde (drei Punktgruppen, zwei schon getroffene
Spieler in einer Gruppe) ist dann eine Auswahl der Engine, kein Ergebnis der einfachen Regel."""

import math
from fractions import Fraction

import pytest

import sga_algorithm as A
import sga_constants as C

RATINGS = (2060.0, 2020.0, 1980.0, 1940.0)
SEEDS = 1500


def _elo(ratings, a: int, b: int) -> Fraction:
    """Elo-Erwartung von Setzplatz a gegen b als exakter Bruch (Fraction(float) ist exakt); die Gegenwahrscheinlichkeit ist genau 1 minus diese."""
    low, high = (a, b) if a < b else (b, a)
    e_low = Fraction(1) / (Fraction(1) + Fraction(10 ** ((ratings[high - 1] - ratings[low - 1]) / 400.0)))
    return e_low if a == low else 1 - e_low


def _place(scores: dict, g: int) -> Fraction:
    return 1 + sum(1 for s, v in scores.items() if v > scores[g]) + Fraction(sum(1 for s, v in scores.items() if s != g and v == scores[g]), 2)


def oracle_place_distribution(ratings, g, gambit_round):
    """Verteilung des Endplatzes von Spieler g: {Platz: Wahrscheinlichkeit}. gambit_round: None (ehrlich), 1 oder 2 (g verliert diese Runde)."""
    def p_win(a, b, rnd):
        if gambit_round == rnd and a == g:
            return Fraction(0)
        if gambit_round == rnd and b == g:
            return Fraction(1)
        return _elo(ratings, a, b)

    dist: dict = {}
    for w1 in (1, 3):
        l1 = 4 - w1                                     # Partie 1-3: der andere der beiden (1 <-> 3)
        for w2 in (2, 4):
            l2 = 6 - w2                                 # Partie 2-4
            p_round1 = p_win(w1, l1, 1) * p_win(w2, l2, 1)
            scores_after_1 = {w1: Fraction(1), w2: Fraction(1), l1: Fraction(0), l2: Fraction(0)}
            for x in ((w1, w2), (w2, w1)):              # Ausgang der Sieger-Partie: x[0] gewinnt
                for y in ((l1, l2), (l2, l1)):          # Ausgang der Verlierer-Partie
                    p = p_round1 * p_win(x[0], x[1], 2) * p_win(y[0], y[1], 2)
                    scores = dict(scores_after_1)
                    scores[x[0]] += 1
                    scores[y[0]] += 1
                    place = _place(scores, g)
                    dist[place] = dist.get(place, Fraction(0)) + p
    return dist


def test_the_oracle_by_hand():
    """Handrechnung mit Stärken, bei denen der Stärkere sicher gewinnt: Setzplatz 1 wird ehrlich Erster; mit Gambit in Runde 1 gewinnen 3 und 2, dann 2 gegen 3 und 1 gegen 4:
    Punkte 1, 2, 1, 0, also Platz 2,5 für Spieler 1. Außerdem: Wahrscheinlichkeiten summieren sich zu 1 bei Stärken, wo alles möglich ist."""
    sure = (8000.0, 6000.0, 4000.0, 2000.0)             # Abstand mindestens 2000 Elo: Erwartung des Stärkeren 0,99999
    honest = oracle_place_distribution(sure, 1, None)
    assert float(honest[1]) == pytest.approx(1.0, abs=1e-3)
    gambit = oracle_place_distribution(sure, 1, 1)
    assert float(gambit[Fraction(5, 2)]) == pytest.approx(1.0, abs=1e-3)
    for g in (1, 2, 3, 4):
        for rnd in (None, 1, 2):
            assert sum(oracle_place_distribution(RATINGS, g, rnd).values()) == 1


@pytest.mark.parametrize("gambit_round", [None, 1, 2])
def test_simulation_matches_the_exact_expectation(gambit_round):
    for g in (1, 2, 3, 4):
        exact = float(sum(p * place for place, p in oracle_place_distribution(RATINGS, g, gambit_round).items()))
        exact_var = float(sum(p * (place - Fraction(exact)) ** 2 for place, p in oracle_place_distribution(RATINGS, g, gambit_round).items()))
        gambit = None if gambit_round is None else A.Gambit(g, gambit_round, C.KIND_LOSE)
        places = [A.standing(A.run_tournament(RATINGS, 2, seed, gambit).players, g)[0] for seed in range(SEEDS)]
        mean = sum(places) / SEEDS
        se = math.sqrt(max(exact_var, 1e-12) / SEEDS)
        assert abs(mean - exact) < 4.5 * se, (g, gambit_round, mean, exact, se)


def test_simulated_place_frequencies_match_the_exact_distribution():
    """Nicht nur der Mittelwert: auch die Anteile der einzelnen Plätze von Setzplatz 1 mit Gambit in Runde 1 (Chi-Quadrat-ähnlich: jeder Anteil in 4,5 Standardfehlern)."""
    exact = oracle_place_distribution(RATINGS, 1, 1)
    places = [A.standing(A.run_tournament(RATINGS, 2, seed, A.Gambit(1, 1, C.KIND_LOSE)).players, 1)[0] for seed in range(SEEDS)]
    for place, p in exact.items():
        share = sum(1 for x in places if Fraction(x) == place) / SEEDS
        se = math.sqrt(float(p) * (1 - float(p)) / SEEDS)
        assert abs(share - float(p)) < 4.5 * se + 1e-9, (place, share, float(p))
    assert {Fraction(x) for x in places} <= set(exact)               # kein Platz in der Simulation, den die Aufzählung nicht kennt


def test_the_gambit_costs_the_strongest_player_places_in_the_tiny_tournament():
    """Folgerung aus dem Orakel: Im 4-Spieler-Turnier mit zwei Runden verschlechtert die Niederlage in Runde 1 den erwarteten Platz von Setzplatz 1
    (Rechnung des Orakels, nicht der Demo)."""
    honest = sum(p * place for place, p in oracle_place_distribution(RATINGS, 1, None).items())
    lost = sum(p * place for place, p in oracle_place_distribution(RATINGS, 1, 1).items())
    assert lost > honest

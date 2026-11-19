"""Szenario: ein Turnierfeld (Elo-Stärken) und die Zufallszahlen der Partien, mit eigenem Zufallsgenerator (SplitMix64).

Zwei Dinge sind bewusst **gemeinsam** für das ehrliche Turnier und das Turnier mit Gambit desselben Feldes:
die Stärken (aus dem Feld-Zufalls-Seed) und die Zufallszahl jeder Partie. Die Zufallszahl hängt nur an (Feld, Runde, Paar der Setzplätze),
nicht an der Reihenfolge, in der die Partien gewürfelt werden: Treffen sich zwei Spieler im ehrlichen Turnier und im Gambit-Turnier in derselben Runde,
würfeln sie dieselbe Zahl. So unterscheiden sich beide Turniere nur dort, wo der Gambit die Paarungen ändert (gemeinsame Zufallszahlen, weniger Rauschen im Vergleich)."""

from __future__ import annotations

import sga_constants as C
from sga_rng import SplitMix64


def expected_score(rating_a: float, rating_b: float) -> float:
    """Elo-Erwartung von A gegen B (Gewinnchance, Remis zählt halb); dieselbe Formel wie `ss_scenario.expected_score` der schweizer-system-demo."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def make_field(n_players: int, spread: float, field_seed: int) -> tuple[float, ...]:
    """Stärken der Spieler 1..n (Setzplatz = Rang nach Stärke, Platz 1 am stärksten): 2000 + spread · z, z standardnormal, absteigend sortiert.
    Dieselben z für jede Streuung: nur die Streuung ändert sich, nicht die Reihenfolge der Spieler."""
    rng = SplitMix64(field_seed)
    raw = sorted((C.BASE_RATING + spread * rng.normal() for _ in range(n_players)), reverse=True)
    return tuple(raw)


def game_uniform(field_seed: int, round_no: int, seat_a: int, seat_b: int) -> float:
    """Zufallszahl in [0, 1) der Partie zwischen den Setzplätzen a und b in einer Runde; symmetrisch in a und b."""
    low, high = (seat_a, seat_b) if seat_a < seat_b else (seat_b, seat_a)
    key = ((field_seed * 64 + round_no) * 64 + low) * 64 + high
    return SplitMix64(key).random()


def low_seat_wins(ratings: tuple[float, ...], field_seed: int, round_no: int, seat_a: int, seat_b: int) -> bool:
    """Gewinnt in dieser Partie der Spieler mit dem kleineren Setzplatz? Ohne Remis: Gewinnchance = Elo-Erwartung (die Elo-Erwartung zählt Remis halb)."""
    low, high = (seat_a, seat_b) if seat_a < seat_b else (seat_b, seat_a)
    return game_uniform(field_seed, round_no, low, high) < expected_score(ratings[low - 1], ratings[high - 1])

"""Kern der Demo: ein Schweizer Turnier (FIDE Dutch, Engine der schweizer-system-demo, hier als wörtliche Kopie `ss_*.py`) mit Elo-Stärken,
in dem ein Spieler in einer frühen Runde absichtlich verliert oder Remis spielt (der „Swiss Gambit“).

Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b): `decide_game` ist die Ergebnisregel einer Partie, `run_tournament` ruft nur
der Reihe nach Paarung, Ergebnis und Eintragung auf, `standing` und `opponent_ratings` sind die Auswertungen, `check_tournament` ist der unabhängige Prüfer."""

from __future__ import annotations

from dataclasses import dataclass

import sga_constants as C
import ss_engine
from sga_scenario import low_seat_wins
from ss_engine import apply_round
from ss_model import Pairing, Player


@dataclass(frozen=True)
class Gambit:
    seat: int          # Setzplatz des Spielers, der absichtlich nicht gewinnt
    round_no: int      # Runde, in der er das tut
    kind: str = C.KIND_LOSE   # C.KIND_LOSE (Niederlage) oder C.KIND_DRAW (Remis)


@dataclass(frozen=True)
class Tournament:
    ratings: tuple[float, ...]            # Stärke des Spielers mit Setzplatz s steht an Stelle s - 1
    rounds: int                           # geplante Rundenzahl
    players: dict                         # Setzplatz -> Player (Endstand)
    pairings: tuple                       # je gespielter Runde ein Tupel von Pairing
    rounds_played: int                    # kann kleiner als `rounds` sein, wenn die Engine keine gültige Paarung fand (Art. 1.9.3)


def decide_game(
    pairing: Pairing, round_no: int, ratings: tuple[float, ...], field_seed: int, gambit: Gambit | None
) -> bool | None:
    """Ergebnis einer Partie aus Sicht von Weiß: True = Weiß gewinnt, False = Schwarz gewinnt, None = Remis.
    Der Gambit-Spieler verliert bzw. remisiert in seiner Gambit-Runde, alle anderen Partien entscheidet die gemeinsame Zufallszahl des Feldes."""
    if gambit is not None and gambit.round_no == round_no and gambit.seat in (pairing.white, pairing.black):
        if gambit.kind == C.KIND_DRAW:
            return None
        return pairing.black == gambit.seat      # Weiß gewinnt genau dann, wenn der Gambit-Spieler Schwarz hat
    lower_wins = low_seat_wins(ratings, field_seed, round_no, pairing.white, pairing.black)
    return lower_wins if pairing.white < pairing.black else not lower_wins


def run_tournament(
    ratings: tuple[float, ...], rounds: int, field_seed: int, gambit: Gambit | None = None
) -> Tournament:
    """Spielt `rounds` Runden Schweizer System (FIDE Dutch). Ohne `gambit` ehrlich, mit `gambit` verliert (remisiert) der Spieler `gambit.seat` in `gambit.round_no`."""
    n = len(ratings)
    if n % 2:
        raise ValueError(f"nur gerade Feldgrößen (kein Freilos): n = {n}")
    if gambit is not None and not (1 <= gambit.seat <= n and 1 <= gambit.round_no <= rounds and gambit.kind in C.KINDS):
        raise ValueError(f"Gambit außerhalb des Turniers: {gambit}")
    players = {seat: Player(rank=seat) for seat in range(1, n + 1)}
    played: list[tuple[Pairing, ...]] = []
    for round_no in range(1, rounds + 1):
        try:
            result = ss_engine.pair_round(players, round_no, total_rounds=rounds)
        except ss_engine.NoValidPairingError:
            break
        white_wins = {p.white: decide_game(p, round_no, ratings, field_seed, gambit) for p in result.pairings}
        players = apply_round(players, result, white_wins)
        played.append(result.pairings)
    return Tournament(ratings=tuple(ratings), rounds=rounds, players=players, pairings=tuple(played), rounds_played=len(played))


def standing(players: dict, seat: int) -> tuple[float, float]:
    """(Endplatz, Punkte) des Spielers: Platz = 1 + Zahl der Spieler mit mehr Punkten + die Hälfte der anderen mit gleich vielen (Gleichstand gemittelt:
    zwei punktgleiche Erste teilen sich 1,5)."""
    score = players[seat].score
    better = sum(1 for p in players.values() if p.score > score)
    tied = sum(1 for p in players.values() if p.score == score and p.rank != seat)
    return 1.0 + better + tied / 2.0, score


def opponent_ratings(t: Tournament, seat: int, after_round: int = 0) -> list[float]:
    """Stärken der Gegner des Spielers in den Runden nach `after_round` (0 = alle Runden), in Rundenfolge."""
    return [t.ratings[g.opponent - 1] for g in t.players[seat].games if g.round_no > after_round and g.opponent != 0]


def check_tournament(t: Tournament) -> list[str]:
    """Unabhängiger Prüfer: Liste der Verstöße (leer = in Ordnung). Jeder Spieler hat in jeder gespielten Runde genau eine Partie, kein Paar trifft sich zweimal,
    die Punkte beider Partner einer Partie ergeben 1, und die Gesamtpunkte sind (Spieler · Runden) / 2."""
    problems: list[str] = []
    n = len(t.ratings)
    for seat, p in t.players.items():
        if len(p.games) != t.rounds_played:
            problems.append(f"Spieler {seat}: {len(p.games)} Partien statt {t.rounds_played}")
        opponents = [g.opponent for g in p.games]
        if len(set(opponents)) != len(opponents):
            problems.append(f"Spieler {seat}: trifft einen Gegner zweimal")
        if abs(p.score - sum(g.score for g in p.games)) > 1e-12:
            problems.append(f"Spieler {seat}: Punktestand passt nicht zu den Partien")
        for g in p.games:
            partner = t.players[g.opponent].games[g.round_no - 1]
            if partner.opponent != seat or abs(partner.score + g.score - 1.0) > 1e-12:
                problems.append(f"Spieler {seat}, Runde {g.round_no}: Gegenpartie passt nicht")
    if abs(sum(p.score for p in t.players.values()) - n * t.rounds_played / 2.0) > 1e-9:
        problems.append("Gesamtpunkte stimmen nicht")
    return problems

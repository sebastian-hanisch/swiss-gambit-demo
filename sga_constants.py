"""Konstanten: Regler-Grenzen, feste Annahmen, Raster der vorgerechneten Messreihen, Farben und Presets.

Rechenaufwand (DEMO-PLAYBOOK §1c): ein Turnier mit der Engine der schweizer-system-demo kostet je nach Feldgröße und Rundenzahl etwa 0,2 bis 2 s
(gemessen 2026-11-18: 16 Spieler 5 Runden 0,17 s, 32 Spieler 7 Runden 1,2 s, 32 Spieler 9 Runden 1,8 s). Die Messreihen (Mittel über 150 bis 300 Felder)
liegen deshalb vorgerechnet in data/gambit_grid.json (tools/make_grid.py); die App rechnet live nur das eine Turnier-Paar (ehrlich/Gambit) des Beispiels.
Am Slider-Maximum (32 Spieler, 9 Runden) sind das zwei Turniere, also einige Sekunden."""

# --- Regler des Live-Beispiels ---------------------------------------------------------------------------------------------------------------------
N_MIN, N_MAX, DEFAULT_N = 16, 32, 32       # gerade Feldgrößen (kein Freilos); N_MAX < 64 ist Voraussetzung der Schlüsselbildung in sga_scenario.game_uniform
N_STEP = 2
ROUNDS_MIN, ROUNDS_MAX, DEFAULT_ROUNDS = 4, 9, 7   # ROUNDS_MIN > GAMBIT_ROUND_MAX: nach der Gambit-Runde bleibt mindestens eine Runde; ROUNDS_MAX <= N_MIN - 1: genug Gegner
SPREAD_MIN, SPREAD_MAX, DEFAULT_SPREAD = 25, 300, 150   # Standardabweichung der Elo-Stärken
SPREAD_STEP = 25
GAMBIT_ROUND_MIN, GAMBIT_ROUND_MAX, DEFAULT_GAMBIT_ROUND = 1, 3, 1
DEFAULT_SEAT = 1
SEED_MAX, DEFAULT_SEED = 999999, 1198   # Feld der Hauptreihe mit der Platzänderung nächst dem Mittel (Setzplatz 1, Runde 1, Niederlage), siehe meta.example im Raster
BASE_RATING = 2000.0                      # Mittelwert der Stärken (wie ss_scenario.BASE_RATING der schweizer-system-demo)
KIND_LOSE, KIND_DRAW = "lose", "draw"
KINDS = (KIND_LOSE, KIND_DRAW)
DEFAULT_KIND = KIND_LOSE
KIND_LABELS = {KIND_LOSE: "absichtlich verlieren (0 Punkte)", KIND_DRAW: "absichtlich Remis spielen (0,5 Punkte)"}
KIND_SHORT = {KIND_LOSE: "verliert", KIND_DRAW: "spielt Remis"}

# --- Raster der Messreihen (tools/make_grid.py, tests/test_grid.py) ---------------------------------------------------------------------------------
GRID_FIELDS_MAIN = 300                    # Felder je Zelle der Hauptmessreihe
GRID_FIELDS_SENS = 150                    # Felder je Zelle der Empfindlichkeitsreihen
GRID_SEED_BASE = 1000                     # Feld-Zufalls-Seeds GRID_SEED_BASE .. GRID_SEED_BASE + Felder - 1; die 150 der Empfindlichkeitsreihen sind die ersten 150 der 300
MAIN = {"n": 32, "rounds": 7, "spread": 150}
MAIN_SEATS = (1, 2, 4, 8, 16, 32)
MAIN_ROUNDS = (1, 2, 3)                   # Runde des absichtlichen Verlierens
SENS_N = (16, 24, 32)
SENS_ROUNDS = (5, 7, 9)
SENS_SPREADS = (50, 100, 150, 200, 300)
SENS_SEAT_NS = (1, 4, 8)                  # Setzplätze der Empfindlichkeitsreihen; dazu der mittlere Platz n/2
HIST_LO, HIST_STEP, HIST_BINS = -33.0, 2.0, 33   # Verteilung der Platzänderung (Gambit minus ehrlich): 33 Klassen der Breite 2, die mittlere (Änderung von -1 bis unter +1) enthält „keine Änderung“


def sens_seats(n: int) -> tuple[int, ...]:
    """Setzplätze der Empfindlichkeitsreihen für ein Feld der Größe n: 1, 4, 8 und die Feldmitte n/2 (ohne Doppelte)."""
    return tuple(sorted(set(SENS_SEAT_NS) | {n // 2}))


# --- Farben ----------------------------------------------------------------------------------------------------------------------------------------
COLOR_HONEST = "#2F6B65"
COLOR_GAMBIT = "#C0504D"
COLOR_NEUTRAL = "rgba(150,150,150,0.55)"
COLOR_LINE = "#4c78a8"

# --- Presets ---------------------------------------------------------------------------------------------------------------------------------------
_BASE = {"n": DEFAULT_N, "rounds": DEFAULT_ROUNDS, "spread": DEFAULT_SPREAD, "seat": DEFAULT_SEAT, "gambit_round": DEFAULT_GAMBIT_ROUND,
         "kind": DEFAULT_KIND, "seed": DEFAULT_SEED}
PRESETS = {
    "Setzplatz 1 verliert Runde 1 (Standard)": dict(_BASE),
    "Mittelfeld (Setzplatz 16) verliert Runde 1": {**_BASE, "seat": 16},
    "Setzplatz 1 verliert erst Runde 3": {**_BASE, "gambit_round": 3},
    "Setzplatz 1 spielt Remis statt zu verlieren": {**_BASE, "kind": KIND_DRAW},
    "Kleines Open (16 Spieler, 5 Runden)": {**_BASE, "n": 16, "rounds": 5, "seat": 1},
    "Enges Feld (Streuung 50)": {**_BASE, "spread": 50},
}
PRESET_HELP = {
    "Setzplatz 1 verliert Runde 1 (Standard)": "Der Fall der Hauptmessreihe: 32 Spieler, 7 Runden, Elo-Streuung 150; der stärkste Spieler verliert Runde 1 absichtlich.",
    "Mittelfeld (Setzplatz 16) verliert Runde 1": "Dasselbe Feld, aber ein Spieler aus der Mitte (Setzplatz 16) verliert Runde 1 absichtlich.",
    "Setzplatz 1 verliert erst Runde 3": "Der Gambit-Spieler verliert erst in Runde 3 absichtlich; die Runden davor spielt er ehrlich, wie im ehrlichen Turnier.",
    "Setzplatz 1 spielt Remis statt zu verlieren": "Statt einer Niederlage ein Remis in Runde 1: ein halber Punkt mehr als bei der Niederlage. Ob die Gegner danach schwächer werden, zeigt Experiment 1 für die Messreihe.",
    "Kleines Open (16 Spieler, 5 Runden)": "Ein kleineres Feld mit 16 Spielern und 5 Runden (Zeile der Empfindlichkeitsreihe zu Feldgröße und Rundenzahl).",
    "Enges Feld (Streuung 50)": "Eng beieinanderliegende Stärken (Elo-Streuung 50): Die Gegner unterscheiden sich weniger in der Stärke, das Ergebnis hängt stärker vom Zufall ab als bei großer Streuung.",
}

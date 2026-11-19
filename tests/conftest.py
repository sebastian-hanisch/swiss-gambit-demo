"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mini():
    """Vier Spieler mit den Stärken 2060, 2020, 1980, 1940 (Setzplatz 1 bis 4). Handrechnung: Runde 1 paart 1 gegen 3 und 2 gegen 4 (obere gegen untere Hälfte);
    in Runde 2 spielen die beiden Sieger gegeneinander und die beiden Verlierer gegeneinander (kein Paar hat sich schon getroffen)."""
    return (2060.0, 2020.0, 1980.0, 1940.0)

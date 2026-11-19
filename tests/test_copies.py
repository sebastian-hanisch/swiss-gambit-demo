"""Die kopierten Dateien (wörtlich, Quelle im Kopf der Datei): Vergleich mit dem Original, solange es im Portfolio-Ordner liegt."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SS = "schweizer-system-demo"
SOURCES = {f"{name}.py": (SS, f"{name}.py") for name in ("ss_blossom", "ss_bracket", "ss_colour", "ss_compat", "ss_engine", "ss_model", "ss_quality")}
SOURCES["sga_rng.py"] = ("sebastianhanisch-website/tools/templates", "rng_splitmix64_exact.py")


@pytest.mark.parametrize("copy", list(SOURCES))
def test_copy_is_verbatim_apart_from_the_header(copy):
    folder, original = SOURCES[copy]
    source = ROOT.parent / folder / original
    if not source.exists():
        pytest.skip("Original liegt nicht im Portfolio-Ordner")
    mine = (ROOT / copy).read_text(encoding="utf-8").splitlines()
    assert mine[0].startswith(f"# Wörtliche Kopie von {folder}/{original}")
    assert mine[1:] == source.read_text(encoding="utf-8").splitlines(), "die Kopie weicht vom Original ab: Änderungen gehören ins Original, danach neu kopieren"


def test_the_copied_engine_runs_on_its_own():
    """Die Kopien reichen für ein Turnier: Runde 1 von acht Spielern paart obere gegen untere Hälfte (Handrechnung: 1-5, 2-6, 3-7, 4-8, Farben beliebig)."""
    import ss_engine
    from ss_model import Player
    result = ss_engine.pair_round({r: Player(rank=r) for r in range(1, 9)}, 1, total_rounds=3)
    assert sorted(tuple(sorted((p.white, p.black))) for p in result.pairings) == [(1, 5), (2, 6), (3, 7), (4, 8)]


def test_the_copied_rng_runs_on_its_own():
    from sga_rng import SplitMix64
    assert SplitMix64(0).next_u64() == 16294208416658607535
    assert SplitMix64(1).below(10) in range(10)


def test_the_scenario_constants_agree_with_the_source_demo():
    """Die Elo-Erwartung und der Mittelwert der Stärken sind in der Quell-Demo `ss_scenario` ebenso festgelegt (dort nicht kopiert: sie lädt die networkx-Engine)."""
    source = ROOT.parent / "schweizer-system-demo" / "ss_scenario.py"
    if not source.exists():
        pytest.skip("Original liegt nicht im Portfolio-Ordner")
    text = source.read_text(encoding="utf-8")
    import sga_constants as C
    from sga_scenario import expected_score
    assert "BASE_RATING = 2000.0" in text and C.BASE_RATING == 2000.0
    assert "return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))" in text
    assert expected_score(2100.0, 2000.0) == pytest.approx(1.0 / (1.0 + 10 ** (-100 / 400.0)))

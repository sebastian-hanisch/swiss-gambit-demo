"""Rechnet die Messreihen vor und schreibt data/gambit_grid.json.

    python tools/make_grid.py                      # volle Messreihen (rund 20 000 s Rechenzeit, auf mehrere Prozesse verteilt)
    python tools/make_grid.py --quick              # kleine Probe zum Ausprobieren (data/gambit_grid_quick.json, nicht für Tests)
    python tools/make_grid.py --cache ORDNER       # Ergebnisse je Feld in ORDNER ablegen und bei einem Neustart wiederverwenden
    python tools/make_grid.py --workers 8          # Zahl der Prozesse (Standard 8)

Alles ist deterministisch (SplitMix64, feste Feld-Zufalls-Seeds ab C.GRID_SEED_BASE). Ein Feld ist eine Aufgabe: das ehrliche Turnier einmal und je Gambit-Variante ein Turnier.
tests/test_grid.py rechnet eine feste Probe nach und vergleicht sie mit der Datei."""

import json
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import sga_constants as C  # noqa: E402
import sga_evaluation as ev  # noqa: E402


def configs(quick: bool) -> list[dict]:
    """Die Konfigurationen der Messreihen: die Hauptreihe (alle Gambit-Varianten) und die Empfindlichkeitsreihen (Runde 1, Niederlage)."""
    m = C.MAIN
    main_variants = tuple((r, k) for r in C.MAIN_ROUNDS for k in C.KINDS)
    if quick:
        return [{"id": "main", "n": 16, "rounds": 5, "spread": 100, "seats": (1, 4), "variants": main_variants[:2], "fields": 4}]
    out = [{"id": "main", "n": m["n"], "rounds": m["rounds"], "spread": m["spread"], "seats": C.MAIN_SEATS, "variants": main_variants, "fields": C.GRID_FIELDS_MAIN}]
    one = ((1, C.KIND_LOSE),)
    for n in C.SENS_N:
        for rounds in C.SENS_ROUNDS:
            if (n, rounds) != (m["n"], m["rounds"]):
                out.append({"id": f"size_{n}_{rounds}", "n": n, "rounds": rounds, "spread": m["spread"], "seats": C.sens_seats(n), "variants": one, "fields": C.GRID_FIELDS_SENS})
    for spread in C.SENS_SPREADS:
        if spread != m["spread"]:
            out.append({"id": f"spread_{spread}", "n": m["n"], "rounds": m["rounds"], "spread": spread, "seats": C.sens_seats(m["n"]), "variants": one, "fields": C.GRID_FIELDS_SENS})
    return out


def _run(task):
    cfg, field_seed, cache = task
    path = Path(cache) / f"{cfg['id']}_{field_seed}.pkl" if cache else None
    if path is not None and path.exists():
        return cfg["id"], field_seed, pickle.loads(path.read_bytes())
    result = ev.field_cells(cfg["n"], cfg["rounds"], cfg["spread"], field_seed, cfg["seats"], cfg["variants"])
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(result))
    return cfg["id"], field_seed, result


def main() -> None:
    args = sys.argv[1:]
    quick = "--quick" in args
    cache = args[args.index("--cache") + 1] if "--cache" in args else None
    workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 8
    t0 = time.time()
    cfgs = configs(quick)
    tasks = [(cfg, fs, cache) for cfg in cfgs for fs in ev.field_seeds(cfg["fields"])]
    per_cfg: dict[str, dict[int, dict]] = {cfg["id"]: {} for cfg in cfgs}
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for cid, fs, result in pool.map(_run, tasks, chunksize=1):
            per_cfg[cid][fs] = result
            done += 1
            if done % 50 == 0:
                print(f"{done}/{len(tasks)} Felder, {time.time() - t0:.0f} s", flush=True)
    cells = []
    for cfg in cfgs:
        ordered = [per_cfg[cfg["id"]][fs] for fs in ev.field_seeds(cfg["fields"])]
        cells += ev.aggregate_config(cfg["n"], cfg["rounds"], cfg["spread"], cfg["seats"], cfg["variants"], ordered)
    main_cfg = cfgs[0]
    main_fields = [per_cfg[main_cfg["id"]][fs] for fs in ev.field_seeds(main_cfg["fields"])]
    example = ev.typical_field(main_fields, ev.field_seeds(main_cfg["fields"]), 1, 1, C.KIND_LOSE) if not quick else None
    grid = {
        "meta": {"example": example, "seed_base": C.GRID_SEED_BASE, "fields_main": C.GRID_FIELDS_MAIN, "fields_sens": C.GRID_FIELDS_SENS,
                 "configs": [{k: v for k, v in cfg.items() if k != "variants"} | {"variants": [list(v) for v in cfg["variants"]]} for cfg in cfgs]},
        "cells": cells,
        "probe": ev.grid_probe(),
    }
    dest = ROOT / "data" / ("gambit_grid_quick.json" if quick else "gambit_grid.json")
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(grid, ensure_ascii=False, indent=None, separators=(",", ":")), encoding="utf-8")
    print(f"{dest} geschrieben: {len(cells)} Zellen aus {len(tasks)} Feldern, {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()

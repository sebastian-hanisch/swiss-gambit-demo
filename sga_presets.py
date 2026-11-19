"""Permalink (Begrenzen), Presets und Zufalls-Seed-Button (Standardmuster aus dem Demo-Portfolio)."""

import random
from dataclasses import dataclass

import streamlit as st

import sga_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None
    choices: tuple | None = None   # nur für Auswahlregler (Art des Gambits)
    step: int = 1


SETTING_SPECS = {
    "n_slider": SettingSpec("n", int, C.DEFAULT_N, C.N_MIN, C.N_MAX, step=C.N_STEP),
    "rounds_slider": SettingSpec("rounds", int, C.DEFAULT_ROUNDS, C.ROUNDS_MIN, C.ROUNDS_MAX),
    "spread_slider": SettingSpec("spread", int, C.DEFAULT_SPREAD, C.SPREAD_MIN, C.SPREAD_MAX, step=C.SPREAD_STEP),
    "seat_slider": SettingSpec("seat", int, C.DEFAULT_SEAT, 1, C.N_MAX),   # die obere Grenze des Reglers ist die gewählte Feldgröße (siehe app.py)
    "gambit_round_slider": SettingSpec("gr", int, C.DEFAULT_GAMBIT_ROUND, C.GAMBIT_ROUND_MIN, C.GAMBIT_ROUND_MAX),
    "kind_radio": SettingSpec("kind", str, C.DEFAULT_KIND, choices=C.KINDS),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
}
PRESET_KEYS = {
    "n": "n_slider", "rounds": "rounds_slider", "spread": "spread_slider", "seat": "seat_slider",
    "gambit_round": "gambit_round_slider", "kind": "kind_radio", "seed": "seed_input",
}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def clamp_seat():
    """Der Setzplatz darf nicht größer sein als das Feld: nach jeder Änderung der Feldgröße (und nach Permalink und Preset) zurücknehmen."""
    n = st.session_state.get("n_slider", C.DEFAULT_N)
    if st.session_state.get("seat_slider", C.DEFAULT_SEAT) > n:
        st.session_state["seat_slider"] = n


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt (Feldgröße auf gerade Werte, Setzplatz auf die Feldgröße)."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            if spec.choices is not None:
                if value not in spec.choices:
                    continue
            else:
                value = min(spec.hi, max(spec.lo, value))
                if spec.step > 1:
                    value = spec.lo + round((value - spec.lo) / spec.step) * spec.step
                    value = min(spec.hi, value)
            st.session_state[state_key] = value
    clamp_seat()
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]
    clamp_seat()


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen
    Standardwert) mit dem Session State. Ein später ergänzter Regler braucht nur seinen Eintrag in SETTING_SPECS,
    dann hebt auch seine Änderung die Markierung auf (tests/test_layout.py prüft das für jeden Regler)."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)

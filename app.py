"""Der Swiss Gambit: lohnt es, im Schweizer System absichtlich zu verlieren? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Ein Turnier-Paar (ehrlich/Gambit) wird live gerechnet; die Messreihen über viele Felder liegen vorgerechnet in data/gambit_grid.json
(tools/make_grid.py). Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sga_constants as C
import sga_evaluation as ev
from sga_layout import dunkles_design, kopf_css
from sga_presets import (
    bounds,
    clamp_seat,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from sga_visualization import (
    build_difference_hist,
    build_example,
    build_main_places,
    build_opponents,
    build_sensitivity,
)

st.set_page_config(page_title="Der Swiss Gambit – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _grid():
    return ev.load_grid()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sga_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("♟️ Der Swiss Gambit: lohnt es, im Schweizer System absichtlich zu verlieren?")
st.markdown(
    """
Im **Schweizer System** spielen in jeder Runde möglichst Spieler mit gleich vielen Punkten gegeneinander. Wer früh verliert, rutscht in eine Gruppe mit weniger Punkten und bekommt dort
vermutlich **schwächere Gegner**, die er leichter schlägt: Das ist die Idee des **Swiss Gambit**. Diese Demo prüft sie an simulierten Turnieren mit der Paarungs-Engine nach
FIDE (Dutch) und stellt jedes Feld **ehrlich gegen Gambit**; das Ergebnis ist eine Messung unter ausdrücklich genannten Annahmen, kein Rat für ein echtes Turnier.

Weiter unten: das Beispiel-Feld, die **🔬 Experimente** (Messreihen über 150 bis 300 Felder), **🚧 Wo die Annahmen enden**, **⚠️ Annahmen, Grenzen und bekannte Probleme**
und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Swiss Gambit", expanded=True):
    st.markdown(
        """
1. **Paarung.** Nach jeder Runde sortiert das Schweizer System die Spieler nach Punkten und paart innerhalb der Punktgruppen (obere gegen untere Hälfte, kein Paar zweimal, Farben möglichst abwechselnd).
   Die Engine ist die der `schweizer-system-demo` (FIDE Dutch, wörtlich kopiert).
2. **Spielstärke.** Jeder Spieler hat eine Elo-Stärke (Normalverteilung um 2000); Setzplatz 1 ist der stärkste. Eine Partie gewinnt der Spieler mit der Elo-Erwartung als Gewinnchance
   (Remis kommen in der Simulation nicht vor, außer dem absichtlichen).
3. **Der Gambit.** Ein gewählter Spieler **verliert in einer frühen Runde absichtlich** (oder spielt Remis). Alle anderen spielen wie gewürfelt.
4. **Der Vergleich ist gepaart.** Dasselbe Feld wird zweimal gespielt, **ehrlich** und **mit Gambit**, mit denselben Stärken und denselben Zufallszahlen je Partie. Verglichen wird der **mittlere Endplatz**
   (Gleichstand gemittelt: zwei punktgleiche Erste teilen sich Platz 1,5) über viele Felder.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Feld und Turnier**")
    n = st.slider("Feldgröße (Spieler)", *bounds("n_slider"), step=C.N_STEP, key="n_slider", on_change=clamp_seat, help="Gerade Zahlen: kein Freilos.")
    rounds = st.slider("Rundenzahl", *bounds("rounds_slider"), key="rounds_slider", help="Runden des Schweizer Systems.")
    spread = st.slider("Elo-Streuung σ", *bounds("spread_slider"), step=C.SPREAD_STEP, key="spread_slider",
                       help="Standardabweichung der Stärken um 2000 Elo. Klein: fast gleich starke Spieler.")
    st.markdown("**Der Gambit**")
    seat = st.slider("Setzplatz des Gambit-Spielers", 1, int(n), key="seat_slider", help="Platz 1 ist der stärkste Spieler des Feldes, Platz n der schwächste.")
    gambit_round = st.slider("Runde des absichtlichen Verlierens", *bounds("gambit_round_slider"), key="gambit_round_slider",
                             help="In dieser Runde verliert (oder remisiert) der Gambit-Spieler absichtlich.")
    kind = st.radio("Art", C.KINDS, format_func=C.KIND_LABELS.get, key="kind_radio", help="Die absichtliche Niederlage zählt 0 Punkte, das Remis 0,5 Punkte, statt des Ergebnisses, das die Partie sonst gehabt hätte.")
    st.markdown("**Zufall**")
    seed = st.number_input("Zufalls-Seed des Beispiel-Felds", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neues Feld würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"n_slider": int(n), "rounds_slider": int(rounds), "spread_slider": int(spread), "seat_slider": int(seat),
                   "gambit_round_slider": int(gambit_round), "kind_radio": kind, "seed_input": int(seed)})

settings = ev.Settings(n=int(n), rounds=int(rounds), spread=int(spread), seat=int(seat), gambit_round=int(gambit_round), kind=kind, seed=int(seed))

# --- Ergebnis: ein Beispiel-Feld ---------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ein Beispiel-Feld")
st.caption("Alle Regler der Seitenleiste wirken hier. Gerechnet werden zwei Turniere (ehrlich und mit Gambit); je nach Feldgröße und Rundenzahl dauert das bis zu einigen Sekunden.")
with st.spinner(f"Rechne zwei Turniere mit {settings.n} Spielern und {settings.rounds} Runden …"):
    a = _analysis(settings)

m1, m2, m3, m4 = st.columns(4)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2): ein größerer Platz ist schlechter.
m1.metric("Endplatz ehrlich", ev.de(a.place_honest, 1), delta="Referenz", delta_color="off")
m2.metric("Endplatz mit Gambit", ev.de(a.place_gambit, 1), delta=f"{ev.signed(a.place_gambit - a.place_honest, 1)} Plätze", delta_color="inverse")
m3.metric("Punkte mit Gambit", ev.de(a.points_gambit, 1), delta=f"{ev.signed(a.points_gambit - a.points_honest, 1)} gegen ehrlich", delta_color="normal")
m4.metric("Gegner im Mittel (Elo)", ev.de(a.opp_gambit, 0), delta=f"{ev.signed(a.opp_gambit - a.opp_honest, 0)} gegen ehrlich", delta_color="off",
          help="Mittlere Elo-Stärke der Gegner über alle Runden. Negativ: Der Gambit hat im Mittel schwächere Gegner gebracht.")
st.plotly_chart(build_example(a), width="stretch", key="example_chart")
st.caption("Ehrlich (grün) gegen Gambit (rot) im selben Feld: oben die Punkte nach jeder Runde, unten die Stärke des jeweiligen Gegners.")

table = []
for r in a.rows:
    def result(score, gambit_game):
        word = {1.0: "Sieg", 0.5: "Remis", 0.0: "Niederlage"}[score]
        return word + (" (absichtlich)" if gambit_game else "")
    table.append({
        "Runde": r.round_no,
        "ehrlich: Gegner (Setzplatz, Elo)": f"{r.opp_honest} ({ev.de(r.elo_honest, 0)})",
        "ehrlich: Ergebnis": result(r.score_honest, False),
        "Gambit: Gegner (Setzplatz, Elo)": f"{r.opp_gambit} ({ev.de(r.elo_gambit, 0)})",
        "Gambit: Ergebnis": result(r.score_gambit, r.round_no == settings.gambit_round),
    })
st.dataframe(table, hide_index=True, width="stretch")
kind_v, text_v = ev.verdict_example(a)
getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------------------

grid = _grid()
if grid is None:
    st.error("Die vorgerechneten Messreihen fehlen (data/gambit_grid.json): `python tools/make_grid.py` erzeugt sie.")
    st.stop()

main_cells = ev.main_cells(grid, settings.gambit_round, settings.kind)
m = C.MAIN

st.markdown("## ❓ Kernfrage: Lohnt der Gambit im Mittel?")
st.caption(f"Messreihe über **{C.GRID_FIELDS_MAIN} gleiche Felder** je Setzplatz: {m['n']} Spieler, {m['rounds']} Runden, Elo-Streuung {m['spread']}. "
           "Die Regler **Runde** und **Art** der Seitenleiste wirken hier; Feldgröße, Rundenzahl, Streuung und Setzplatz gelten nur für das Beispiel-Feld oben.")
st.plotly_chart(build_main_places(main_cells, settings.seat), width="stretch", key="main_chart")
kind_m, text_m = ev.verdict_main(main_cells)
getattr(st, kind_m)(text_m)
kind_w, text_w = ev.verdict_win(main_cells)
getattr(st, kind_w)(text_w)

chosen = next((c for c in main_cells if c["seat"] == settings.seat), None)
if chosen is None:
    st.caption(f"Setzplatz {settings.seat} liegt nicht in der Messreihe (Setzplätze {', '.join(map(str, C.MAIN_SEATS))}).")
else:
    f = chosen["fields"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Platz {chosen['seat']}: Endplatz ehrlich", ev.de(chosen["hp"]), delta="Referenz", delta_color="off")
    c2.metric("Endplatz mit Gambit", ev.de(chosen["gp"]), delta=f"{ev.signed(ev.d_mean(chosen))} ± {ev.de(ev.SE_FACTOR * ev.d_se(chosen))} (2 SE)", delta_color="inverse")
    c3.metric("Alleiniger Turniersieg ehrlich / Gambit", f"{ev.pct(chosen['top1_h'] / f)} / {ev.pct(chosen['top1_g'] / f)}",
              help="Anteil der Felder, in denen der Spieler allein Erster ist (Platz 1,0; ein geteilter erster Platz zählt nicht). "
                   f"Gepaart: nur mit Gambit {chosen['top1_gain']} Felder, nur ehrlich {chosen['top1_loss']} Felder.")
    c4.metric("Punkte ehrlich / Gambit", f"{ev.de(chosen['hpts'])} / {ev.de(chosen['gpts'])}")
    st.caption(f"Gambit besser in {chosen['better']}, gleich in {chosen['equal']}, schlechter in {chosen['worse']} von {f} Feldern.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Bringt der Gambit schwächere Gegner?")
st.caption("Mittlere Elo-Stärke der Gegner je Setzplatz (dieselbe Messreihe wie oben, gleiche Regler **Runde** und **Art**). Die zweite Abbildung zählt nur die Runden nach der Gambit-Runde.")
tab_all, tab_after = st.tabs(["Alle Runden", "Nur Runden nach der Gambit-Runde"])
with tab_all:
    st.plotly_chart(build_opponents(main_cells, after=False), width="stretch", key="opp_all_chart")
with tab_after:
    st.plotly_chart(build_opponents(main_cells, after=True), width="stretch", key="opp_after_chart")
kind_o, text_o = ev.verdict_opponents(main_cells)
getattr(st, kind_o)(text_o)

st.subheader("🔬 Experiment 2: Wie verteilt sich die Wirkung über die Felder?")
hist_seat = st.selectbox("Setzplatz der Messreihe", C.MAIN_SEATS, index=0, key="hist_seat", format_func=lambda s: f"Setzplatz {s}")
hist_cell = next(c for c in main_cells if c["seat"] == hist_seat)
st.plotly_chart(build_difference_hist(hist_cell), width="stretch", key="hist_chart")
d_med = hist_cell["d_median"]
st.info(
    f"Setzplatz {hist_seat}, Runde {hist_cell['round']}, {C.KIND_SHORT[hist_cell['kind']]}: Mittel der Platzänderung {ev.signed(ev.d_mean(hist_cell))}, "
    f"Median {ev.signed(d_med)}, Standardabweichung {ev.de(hist_cell['d_sd'])} Plätze über {hist_cell['fields']} Felder. "
    f"Gambit besser in {hist_cell['better']}, gleich in {hist_cell['equal']}, schlechter in {hist_cell['worse']} Feldern."
)

st.subheader("🔬 Experiment 3: Hängt es an Feldgröße und Rundenzahl?")
st.caption("Runde 1, absichtlich verlieren; Elo-Streuung 150; je Zelle 150 Felder (Zelle mit 32 Spielern und 7 Runden: 300). Balken: ±2 Standardfehler. "
           "Bei 16 Spielern ist Platz 8 die Feldmitte.")
size_cells = ev.sens_cells(grid, "size")
st.plotly_chart(build_sensitivity(size_cells, "size"), width="stretch", key="sens_size_chart")
kind_s, text_s = ev.verdict_sens(size_cells, "size")
getattr(st, kind_s)(text_s)

st.subheader("🔬 Experiment 4: Hängt es an der Elo-Streuung?")
st.caption("Runde 1, absichtlich verlieren; 32 Spieler, 7 Runden; je Zelle 150 Felder (σ = 150: 300). Balken: ±2 Standardfehler.")
spread_cells = ev.sens_cells(grid, "spread")
st.plotly_chart(build_sensitivity(spread_cells, "spread"), width="stretch", key="sens_spread_chart")
kind_p, text_p = ev.verdict_sens(spread_cells, "spread")
getattr(st, kind_p)(text_p)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Eine einfache Strategie:** feste Runde, feste Art, der Spieler wählt keinen Gegner | Ein gezielter Gambit (Zeitpunkt und Gegnerwahl nach dem Stand des Turniers) ist **nicht gemessen**; laut Suchausschnitten der Literatur (nicht im Volltext gelesen) kann sich ein Gambit unter bestimmten Bedingungen lohnen | `schweizer-system-demo` (die Paarung selbst), Literaturhinweis unten |
| **Elo-Erwartung ohne Remis** (Gewinnchance = Erwartung) | Echte Schachturniere haben viele Remis; wie der Gambit dann wirkt, ist **nicht gemessen** | – |
| **Fester Tiebreak = Punkte, Gleichstand gemittelt** | Wertungen wie Buchholz ordnen Gleichstände anders; der Gambit kann dort eine andere Wirkung haben. Nicht gemessen | – |
| **Bewertung nach dem mittleren Endplatz** | Wer nur den Turniersieg oder einen Preis sucht, bewertet anders; die Chance auf Platz 1 steht deshalb daneben. Ein Preis in der Mitte der Tabelle ist nicht gemessen | `bracket-seeding-demo` (Setzliste und Siegchance im K.-o.-System) |
| **Alle anderen spielen ehrlich** | Wenn mehrere absichtlich verlieren oder sich absprechen, ändert sich das Feld; das ist ein anderes Modell | `algorithmische-kollusion-demo` (Absprachen), „Wann lohnt Verlieren?“ (Anreize bei mitgenommenen Punkten) |
| **Elo-Stärken normalverteilt, 16 bis 32 Spieler, 4 bis 9 Runden** | Andere Felder (etwa ein Open mit 200 Spielern und 9 Runden) sind nicht gemessen | – |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(
        f"""
**Annahmen.** Stärken: 2000 + σ · z mit z standardnormal, nach Stärke sortiert zu Setzplätzen. Partie: der Spieler mit der größeren Elo-Zahl gewinnt mit der Elo-Erwartung, es gibt kein Remis außer dem absichtlichen.
Paarung: FIDE Dutch in der Fassung der `schweizer-system-demo` (Regeltext-Modus). Die Zufallszahl einer Partie hängt nur von (Feld, Runde, Paar der Setzplätze); so spielen sich zwei Spieler, die sich in beiden Turnieren treffen, dieselbe Zufallszahl.
Messreihen: {C.GRID_FIELDS_MAIN} Felder in der Hauptreihe, {C.GRID_FIELDS_SENS} in den Empfindlichkeitsreihen, Feld-Zufalls-Seeds ab {C.GRID_SEED_BASE}.

**Grenzen.** Gemessen ist nur die **einfache Strategie** (feste Runde, feste Art) und nur der **mittlere Endplatz** (dazu die Chance auf Platz 1 und auf einen Platz unter den ersten drei). Gezielte Gambits, andere Tiebreaks, Remis in den Partien, Absprachen und große Felder sind nicht gemessen.
„Gesichert“ heißt hier: Das Mittel der Platzänderung liegt mehr als zwei Standardfehler von null entfernt (Standardfehler über die Felder, gepaart); das ist eine Lesehilfe, kein Test mit Korrektur für die vielen Zellen.

**Bekannte Probleme und Unsicherheiten.** Die Messreihen sind vorgerechnet und ändern sich nicht mit den Reglern; nur das Beispiel-Feld oben rechnet live. Ein Beispiel-Feld ist ein Einzelfall.
Die Engine kann bei wenigen Spielern und vielen Runden keine gültige Paarung finden; das Beispiel meldet das, die Messreihen enthalten solche Fälle nicht (der Erzeuger bricht dann ab). Die Plotly-Abbildungen sind nur im AppTest, nicht im Browser geprüft.
        """
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** sind $n$ Spieler mit Stärken $R_1 \ge \dots \ge R_n$ (Setzplatz $s$ hat die Stärke $R_s$), eine Rundenzahl $T$ und die Paarungsregel $\Pi$ (FIDE Dutch): $\Pi$ ordnet dem Stand nach $t-1$ Runden die Paarungen der Runde $t$ zu.
**Gesucht** ist der mittlere Endplatz eines Spielers $g$ ehrlich und mit Gambit.

| Symbol | Bedeutung |
|---|---|
| $n$, $T$ | Zahl der Spieler (gerade), Zahl der Runden |
| $R_s$ | Elo-Stärke des Spielers mit Setzplatz $s$, $R_s = 2000 + \sigma z_{(s)}$ ($z_{(s)}$ die absteigend sortierten Standardnormalwerte) |
| $g$, $r$ | Setzplatz des Gambit-Spielers, Runde des Gambits |
| $P_t(g)$ | Punkte von $g$ nach Runde $t$; $P_T(g)$ am Ende |
| $\mathrm{Platz}(g)$ | Endplatz, Gleichstand gemittelt |

**Partie.** Die Gewinnchance des Spielers $a$ gegen $b$ ist die Elo-Erwartung
$$E(a,b) = \frac{1}{1 + 10^{(R_b - R_a)/400}}.$$
Ohne Gambit gewinnt $a$ mit Wahrscheinlichkeit $E(a,b)$, sonst $b$; es gibt kein Remis. Im Gambit-Turnier verliert $g$ in Runde $r$ (Punkte 0) oder remisiert (0,5), alle anderen Partien bleiben wie beschrieben.

**Endplatz.** Mit $P_T(i)$ den Endpunkten aller Spieler:
$$\mathrm{Platz}(g) = 1 + \bigl|\{ i : P_T(i) > P_T(g) \}\bigr| + \tfrac12\,\bigl|\{ i \ne g : P_T(i) = P_T(g) \}\bigr|.$$

**Platzänderung.** Für ein Feld $\omega$ (Stärken und Zufallszahlen aller Partien) ist $\Delta(\omega) = \mathrm{Platz}_{\text{Gambit}}(g;\omega) - \mathrm{Platz}_{\text{ehrlich}}(g;\omega)$, positiv heißt schlechter. Die Messreihe schätzt das Mittel und seinen Standardfehler über $F$ Felder
$$\bar\Delta = \frac1F \sum_{f=1}^{F} \Delta(\omega_f)$$
$$\mathrm{SE} = \frac{s_\Delta}{\sqrt F}$$
mit der Standardabweichung $s_\Delta$ der $\Delta(\omega_f)$.
**Gesichert** heißt $|\bar\Delta| > 2\,\mathrm{SE}$. Beide Turniere desselben Feldes nutzen dieselben Stärken und je Partie dieselbe Zufallszahl $u(\omega, t, \{a, b\}) \in [0,1)$ (SplitMix64, nur von Feld, Runde und Paar abhängig).

**Orakel.** Für $n = 4$, $T = 2$ lässt sich $\mathbb E[\mathrm{Platz}(g)]$ durch Aufzählen aller Ergebnisse berechnen (die Paarung der zweiten Runde ist dann Sieger gegen Sieger und Verlierer gegen Verlierer); der Test vergleicht die Simulation damit.

**Literatur** (nur nach Suchausschnitten bekannt, nicht im Volltext gelesen): Cseh, Führlich, Lenzner, „The Swiss Gambit“ (arXiv 2302.10595).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Wettbewerbsverzerrung: Reihenfolge und Anreize](https://sebastianhanisch.net/konzepte-wettbewerbsverzerrung.html)."
)

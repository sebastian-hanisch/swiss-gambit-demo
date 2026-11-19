# Der Swiss Gambit: lohnt es, im Schweizer System absichtlich zu verlieren? – Streamlit-Demo

<!-- Live-Link nach dem Deploy hierher setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-swiss-gambit-demo.streamlit.app/)** -->

Konzepte-Demo für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Teil der Linie „Wettbewerbsverzerrung erklärt“ (Bereich Wertung und Wahl), Ast **Anreize**: Wenn ein Regelwerk Spielern erlaubt, ihr Ergebnis selbst zu beeinflussen, lohnt sich das dann?
Vehikel ist das **Schweizer System** mit der Paarungs-Engine der `schweizer-system-demo` (FIDE Dutch, wörtlich kopiert) und **Elo-Feldern**: 32 Spieler, 7 Runden, Stärken normalverteilt um 2000 mit Streuung 150. Ein gewählter Spieler **verliert in einer frühen Runde absichtlich**
(der **Swiss Gambit**) in der Hoffnung, danach schwächere Gegner zu bekommen und am Ende besser zu stehen. Die Demo stellt dasselbe Feld **ehrlich gegen Gambit** (gleiche Stärken, gleiche Zufallszahlen je Partie) und vergleicht den **mittleren Endplatz** über viele Felder.
**Gemessen ist nur die einfache Strategie unter den Annahmen dieser README; ein Rat für ein echtes Turnier ist das nicht.**

## Ergebnis in Kürze

Alle Zahlen: Mittel über 300 gleiche Felder (Feld-Zufalls-Seeds 1000 bis 1299), 32 Spieler, 7 Runden, Elo-Streuung 150, Gleichstand beim Endplatz gemittelt, Remis kommen in den Partien nicht vor (außer dem absichtlichen).

- **Im Mittel schadet die einfache Strategie in den meisten Zellen (Setzplatz 32 mit Remis nützt).** Über alle 36 Zellen der Hauptreihe (3 Gambit-Runden × 2 Arten × 6 Setzplätze) ist der mittlere Endplatz mit Gambit in **31 von 36** Zellen gesichert schlechter als ehrlich, in 3 gesichert besser und in 2 offen
  (Gesichert besser nur in: Setzplatz 32, Runde 1, Remis; Setzplatz 32, Runde 2, Remis; Setzplatz 32, Runde 3, Remis). Bei Niederlage in Runde 1 liegt die Verschlechterung für Setzplatz 1, 2, 4, 8, 16 und 32 zwischen +0,45 und +2,13 Plätzen (Tabelle unten).
- **Er bringt schwächere Gegner, aber nicht genug.** Bei Niederlage in Runde 1 sind die Gegner im Mittel schwächer in 6 von 6 Setzplätzen (alle Runden), in 6 von 6 (nach der Gambit-Runde); beim Remis in Runde 1 in 3 von 6 bzw. 3 von 6.
  Die Punkte liegen im Mittel niedriger in 18 von 18 Zellen mit Niederlage und in 15 von 18 Zellen mit Remis; dass der Gewinn an Gegnerstärke den Punktverlust der absichtlichen Partie nicht aufwiegt, ist die Lesart dieser Zahlen, keine Ursachenmessung.
- **Die Spitze: bei Niederlage sinkt auch sie gesichert; bei Remis ist der alleinige Turniersieg nicht gesichert häufiger, Platz 1 bis 3 aber in einem Teil der Setzplätze.** Alleiniger Turniersieg Setzplatz 1, Runde 1: Niederlage 42 → 4 von 300 (nur Gambit 4, nur ehrlich 42; seltener); Remis 42 → 51 von 300 (nur Gambit 38, nur ehrlich 29; offen). Setzplatz 2 mit Remis: 17 → 27 von 300 (nur Gambit 22, nur ehrlich 12; offen).
  Über die Setzplätze, Runde 1: Niederlage in 0 häufiger, 3 seltener, 3 offen; Remis in 0 häufiger, 0 seltener, 6 offen (alleiniger Turniersieg, gepaart gezählt). Bei Niederlage sinkt die Zahl der alleinigen Turniersiege gesichert; bei Remis ist der Unterschied nicht gesichert (die ungepaarten Zählungen steigen bei Setzplatz 1 und 2, gepaart ist der Abstand klein gegen seine Streuung).
  Platz 1 bis 3 mit Remis: in Runde 1 in 2 von 6 Setzplätzen gesichert häufiger (Setzplatz 1: 138 → 170 von 300 Feldern), in Runde 2 in 1 von 6, in Runde 3 in 2 von 6; bei Niederlage in Runde 1 in 5 von 6 gesichert seltener (Setzplatz 1: 138 → 75). Gezählt wie beim Turniersieg, gepaart, als Vorzeichentest-Näherung.
- **Ein einzelnes Feld täuscht.** Setzplatz 1, Runde 1, Niederlage: Median +0,25 Plätze, Mittel +2,13; Gambit besser in 69, gleich in 81, schlechter in 150 von 300 Feldern.
- **Bei Niederlage in Runde 1 bleibt das Vorzeichen über Feldgröße, Rundenzahl und Streuung im gemessenen Bereich** (Setzplätze 1, 4, 8 und Feldmitte, je Zelle 150 Felder): 31 von 33 Zellen (Feldgröße und Rundenzahl) und 17 von 20 Zellen (Elo-Streuung) sind gesichert schlechter, 0 bzw. 0 gesichert besser (Änderung +0,66 bis +3,78 Plätze bzw. -0,02 bis +4,78 Plätze). Die Größe bleibt nicht gleich: die drei offenen Zellen der Streuungsreihe liegen bei Streuung 200 (Feldmitte) und 300 (Setzplatz 8 und Feldmitte).

## Warum dieses Problem

Im Schweizer System spielen in jeder Runde möglichst Spieler mit gleich vielen Punkten gegeneinander. Wer früh verliert, landet in einer Punktgruppe mit schwächeren Gegnern, so die Idee des Swiss Gambit; wer als Favorit anfängt, hofft, die Punkte später billig nachzuholen. Ob das stimmt, ist eine
Frage an die Paarungsregel, nicht an das Gefühl: Die Demo rechnet sie mit der echten Paarungs-Engine nach, auf vielen Feldern und mit gemeinsamen Zufallszahlen, damit der Vergleich nicht im Rauschen untergeht. Das Ergebnis für diese einfache Strategie ist ein **ehrlicher Negativbefund**.

## Befunde und Korrekturen gegenüber dem Plan

Der Plan (Notiz zur Linie, Vormessung M5, nicht in diesem Repo) nannte für 32 Spieler, 7 Runden, Elo-Streuung 150 und 300 gleiche Felder (Python-`random`, Zufallszahlen in der Reihenfolge der Partien): ehrlich 4,59 / 7,55 / 10,17 / 15,56 gegen Gambit 6,32 / 9,57 / 11,40 / 17,41 für Setzplatz 1 / 4 / 8 / 16
und den Befund, dass die einfache Strategie in allen vier Fällen um 1,2 bis 2,0 Plätze schadet. Neu gemessen (SplitMix64, gemeinsame Zufallszahl je Partie, 300 Felder): siehe die erste Tabelle unten. Abweichungen und Ergänzungen:

- **Richtung bestätigt, Größe leicht anders.** Neu gemessen, Niederlage in Runde 1 (Setzplatz 1 / 4 / 8 / 16): ehrlich 4,42 / 7,61 / 9,68 / 15,23 gegen Gambit 6,55 / 9,57 / 11,75 / 17,13, also Änderungen von +2,13 / +1,96 / +2,06 / +1,89 Plätzen statt der +1,73 / +2,02 / +1,23 / +1,85 der Vormessung (aus deren Zahlen gerechnet). Der Gambit schadet in allen vier Setzplätzen, wie die Vormessung es erwarten ließ; die Vormessung nannte „1,2 bis 2,0 Plätze“, hier sind es +1,89 bis +2,13. Der Unterschied liegt bei Setzplatz 8 am größten; die Standardfehler dieser Reihe sind 0,30 bis 0,46 Plätze, andere Felder und anderer Zufallsgenerator genügen also als Erklärung (eine Deutung, nicht eigens geprüft).
- **Andere Zufallszahlen.** Die Vormessung würfelte die Partien in der Reihenfolge der Paarungen (Python-`random`); hier hängt die Zufallszahl einer Partie nur an (Feld, Runde, Paar der Setzplätze), und der Generator ist SplitMix64 (plattformfest). Ehrlich und Gambit spielen dadurch dieselben Zahlen, wo sich dieselben Spieler treffen; die Zahlen sind nicht Zelle für Zelle mit der Vormessung vergleichbar.
- **Neu gegenüber der Vormessung:** Gambit in Runde 2 und 3, die Art Remis, die Gegnerstärke, die Chance auf den alleinigen Turniersieg und auf Platz 1 bis 3, die Verteilung über die Felder, Setzplatz 2 und 32, Feldgrößen 16 und 24, Rundenzahlen 5 und 9, Streuungen 50, 100, 200 und 300. Zur Siegchance fand sich: Niederlage in Runde 1 senkt die alleinigen Turniersiege von Setzplatz 1 gesichert (42 → 4 von 300 (nur Gambit 4, nur ehrlich 42; seltener)); Remis nicht gesichert (42 → 51 von 300 (nur Gambit 38, nur ehrlich 29; offen)). In der Vormessung stand dazu nichts.
- **„Remis“ in der Vormessung** meinte den gemittelten Gleichstand beim Endplatz; Remis in den Partien gab es dort ebenso wenig wie hier (außer dem absichtlichen der Art „Remis“).
- **`ss_scenario.py` nicht kopiert.** Der Auftrag sah die Kopie der nötigen `ss_*.py` vor; `ss_scenario.py` zieht die Matching-Engine und damit networkx nach, die Paarung braucht sie nicht. Elo-Erwartung und Mittelwert der Stärken (2000) sind in `sga_scenario.py` und `sga_constants.py` neu geschrieben; `tests/test_copies.py` prüft beides gegen den Text der Quelle.
- **Feldgrößen nur gerade (16 bis 32).** Die Vormessung rechnete nur mit 32 Spielern; bei ungerader Zahl bekäme einer ein Freilos, das hier nicht modelliert ist.

## Modell

Gegeben sind $n$ Spieler mit Elo-Stärken $R_1 \ge \dots \ge R_n$ (Setzplatz $s$ hat die Stärke $R_s$; $R = 2000 + \sigma z$ mit $z$ standardnormal) und $T$ Runden. Die Paarung jeder Runde bestimmt die Engine nach dem Stand (FIDE Dutch: Punktgruppen, obere gegen untere Hälfte, kein Paar zweimal, Farbausgleich).
Eine Partie gewinnt Spieler $a$ gegen $b$ mit Wahrscheinlichkeit $E(a,b) = 1 / (1 + 10^{(R_b - R_a)/400})$ (Elo-Erwartung); Remis kommen in der Simulation nicht vor. Der **Gambit** setzt das Ergebnis einer Partie des Spielers $g$ in Runde $r$ auf Niederlage (0 Punkte) oder Remis (0,5 Punkte).
Der Endplatz ist $1 + |\{i : P_i > P_g\}| + \tfrac12 |\{i \ne g : P_i = P_g\}|$ (Gleichstand gemittelt). Die Platzänderung $\Delta = \mathrm{Platz}_{\text{Gambit}} - \mathrm{Platz}_{\text{ehrlich}}$ ist positiv, wenn der Gambit schadet. Der 📐-Expander der App enthält die Formeln.

**Gemeinsame Zufallszahlen.** Die Zufallszahl einer Partie hängt nur von (Feld, Runde, Paar der Setzplätze), nicht von der Reihenfolge des Würfelns: Treffen sich zwei Spieler im ehrlichen und im Gambit-Turnier in derselben Runde, würfeln sie dieselbe Zahl. So unterscheiden sich beide Turniere nur dort, wo der Gambit die Paarungen ändert.

## Methodik

- **Turnier.** `run_tournament` (`sga_algorithm.py`) ruft je Runde `ss_engine.pair_round` (kopiert) und trägt die Ergebnisse mit `ss_engine.apply_round` ein; `decide_game` setzt das Ergebnis des Gambit-Spielers in seiner Gambit-Runde, alle anderen Partien entscheidet die gemeinsame Zufallszahl.
- **Endplatz, Gegnerstärke.** `standing` zählt den Platz (Gleichstand gemittelt), `opponent_ratings` liefert die Stärken der Gegner; „Gegner im Mittel (Elo)“ ist ihr Mittel über alle gespielten Runden, „nach der Gambit-Runde“ nur die Runden nach `r`. Die Partie des Gambits selbst (der Gegner, der den absichtlichen Sieg bekommt) zählt in „alle Runden“ mit.
- **Messreihen.** `tools/make_grid.py` rechnet je Feld das ehrliche Turnier einmal und je Gambit-Variante ein Turnier und schreibt `data/gambit_grid.json` (vorgerechnet, die App liest nur). Hauptreihe: 32 Spieler, 7 Runden, Streuung 150, Setzplätze 1, 2, 4, 8, 16, 32, Gambit-Runde 1 bis 3, Niederlage und Remis, je Zelle 300 Felder.
  Empfindlichkeitsreihen (Runde 1, Niederlage, je Zelle 150 Felder, die ersten 150 der 300): Feldgröße 16, 24, 32 × Rundenzahl 5, 7, 9 (Streuung 150) und Streuung 50, 100, 150, 200, 300 (32 Spieler, 7 Runden); Setzplätze 1, 4, 8 und die Feldmitte. Die Zellen mit 32 Spielern, 7 Runden und Streuung 150 kommen aus der Hauptreihe (300 Felder).
  Wanduhrzeit der Messreihen: 3386 s mit 10 Prozessen (gemessen beim Bau auf einem ausgelasteten Rechner, nicht verallgemeinerbar).
- **„Gesichert“.** Das Mittel der Platzänderung liegt mehr als zwei Standardfehler von null entfernt (Standardfehler über die Felder, gepaart). Das ist eine Lesehilfe, keine Korrektur für die vielen Zellen.
- **Live-Beispiel.** Ein Feld, zwei Turniere (ehrlich/Gambit), gemessen beim Bau auf einem ausgelasteten Rechner: 0,4 s (16 Spieler, 5 Runden) bis 3,7 s (32 Spieler, 9 Runden); dieselbe Rechnung wie je Feld der Messreihen (`field_cells`, Test `test_grid.py`). Das Beispiel-Feld der Voreinstellung ist das Feld der Hauptreihe, dessen Platzänderung für Setzplatz 1 (Runde 1, Niederlage) dem Mittel am nächsten liegt: Seed 1198, Platz 2,0 ehrlich, Platz 4,5 mit Gambit
  (Mittel aller Felder +2,13); gewählt nach dem Mittel, nicht nach dem Aussehen.

## Befunde (gemessen, keine Behauptungen)

Bedingungen stehen in jeder Überschrift. Jede Tabellenzeile und jede Kernzahl dieses Abschnitts und der Ergebnis-Übersicht berechnet `tests/test_claims.py` aus `data/gambit_grid.json` und sucht sie wörtlich in dieser README; die Messreihe selbst sichern `tests/test_grid.py` (Aufbau, Probe wird nachgerechnet) und das Orakel. **Nicht durch Tests belegt:** die Zahlen der Vormessung (Notiz, nicht in diesem Repo), die Wanduhrzeit der Messreihen und die Rechenzeit des Live-Beispiels (Messungen beim Bau auf einem ausgelasteten Rechner).

**Hauptreihe: Niederlage in Runde 1** (32 Spieler, 7 Runden, Streuung 150, 300 gleiche Felder je Zelle; Änderung = Gambit minus ehrlich, ± zwei Standardfehler; Test `test_every_table_row_of_the_readme_is_computed_from_the_grid`):

| Setzplatz | Endplatz ehrlich | Endplatz Gambit | Änderung | Urteil | Punkte ehrlich / Gambit |
|---|---|---|---|---|---|
| 1 | 4,42 | 6,55 | +2,13 ± 0,61 | schlechter | 5,45 / 4,91 |
| 2 | 6,12 | 8,06 | +1,94 ± 0,71 | schlechter | 5,08 / 4,66 |
| 4 | 7,61 | 9,57 | +1,96 ± 0,68 | schlechter | 4,77 / 4,41 |
| 8 | 9,68 | 11,75 | +2,06 ± 0,84 | schlechter | 4,43 / 4,11 |
| 16 | 15,23 | 17,13 | +1,89 ± 0,93 | schlechter | 3,67 / 3,41 |
| 32 | 28,66 | 29,11 | +0,45 ± 0,27 | schlechter | 1,52 / 1,40 |

**Urteile über alle Gambit-Runden und Arten** (je Zeile 6 Setzplätze; „schlechter / offen / besser“ = Zahl der Setzplätze, in denen der Gambit gesichert schlechter ist, sich nicht von null unterscheidet oder gesichert besser ist; Änderung = kleinste bis größte mittlere Platzänderung; letzte Spalte: Zahl der Setzplätze, in denen der Gambit den alleinigen Turniersieg in gesichert mehr, offen vielen oder gesichert weniger Feldern erreicht, gepaart gezählt, Vorzeichentest-Näherung mit zwei Wurzeln aus der Zahl der abweichenden Felder; Setzplätze ohne Turniersieg zählen als offen):

| Gambit-Runde | Art | schlechter | offen | besser | Änderung | Alleiniger Sieg: häufiger / offen / seltener |
|---|---|---|---|---|---|---|
| 1 | Niederlage | 6 | 0 | 0 | +0,45 bis +2,13 | 0 / 3 / 3 |
| 1 | Remis | 5 | 0 | 1 | -0,90 bis +2,62 | 0 / 6 / 0 |
| 2 | Niederlage | 6 | 0 | 0 | +0,42 bis +2,70 | 0 / 3 / 3 |
| 2 | Remis | 4 | 1 | 1 | -1,12 bis +2,67 | 0 / 6 / 0 |
| 3 | Niederlage | 6 | 0 | 0 | +0,43 bis +2,55 | 0 / 3 / 3 |
| 3 | Remis | 4 | 1 | 1 | -0,99 bis +1,90 | 0 / 6 / 0 |

Das sind zusammen 36 Zellen: in **31 von 36** Zellen gesichert schlechter, 3 gesichert besser, 2 offen.

**Gegnerstärke** (Elo, Runde 1, 32 Spieler, 7 Runden, Streuung 150, 300 Felder; ehrlich / Gambit, dann Änderung; „nach der Gambit-Runde“ = Runden 2 bis 7):

| Art | Setzplatz | Gegner alle Runden | Änderung | Gegner nach der Gambit-Runde | Änderung |
|---|---|---|---|---|---|
| Niederlage | 1 | 2073 / 2023 | -51 | 2087 / 2027 | -59 |
| Niederlage | 2 | 2064 / 2010 | -54 | 2078 / 2015 | -63 |
| Niederlage | 4 | 2033 / 1988 | -46 | 2046 / 1993 | -53 |
| Niederlage | 8 | 2014 / 1961 | -53 | 2032 / 1970 | -62 |
| Niederlage | 16 | 1984 / 1918 | -66 | 2034 / 1957 | -77 |
| Niederlage | 32 | 1928 / 1916 | -12 | 1915 / 1902 | -14 |
| Remis | 1 | 2073 / 2064 | -9 | 2087 / 2076 | -11 |
| Remis | 2 | 2064 / 2059 | -5 | 2078 / 2072 | -6 |
| Remis | 4 | 2033 / 2041 | +8 | 2046 / 2055 | +9 |
| Remis | 8 | 2014 / 2021 | +7 | 2032 / 2040 | +8 |
| Remis | 16 | 1984 / 1963 | -21 | 2034 / 2009 | -25 |
| Remis | 32 | 1928 / 1942 | +14 | 1915 / 1931 | +16 |

Niederlage in Runde 1: Gegner im Mittel schwächer in 6 von 6 Setzplätzen (alle Runden), in 6 von 6 (nach der Gambit-Runde); Änderung bei Niederlage zwischen -66 und -12 Elo (alle Runden).
Remis in Runde 1: Gegner im Mittel schwächer in 3 von 6 Setzplätzen (alle Runden), in 3 von 6 (nach der Gambit-Runde).

**Verteilung** (Setzplatz 1, Runde 1, Niederlage, 300 Felder): Mittel +2,13 Plätze, Median +0,25, Standardabweichung 5,25; Gambit besser in 69, gleich in 81, schlechter in 150 Feldern. Punkte 5,45 / 4,91 (ehrlich / Gambit). Turniersieg 14,0 % / 1,3 %, Platz 1 bis 3 46,0 % / 25,0 % (ehrlich / Gambit; Gleichstand gemittelt, „Platz höchstens k“).

**Empfindlichkeit: Feldgröße und Rundenzahl** (Runde 1, Niederlage, Streuung 150; Änderung ± zwei Standardfehler):

| Feld | Felder | Setzplatz 1 | Setzplatz 4 | Setzplatz 8 | Feldmitte (n/2) |
|---|---|---|---|---|---|
| 16 Spieler, 5 Runden | 150 | +2,00 ± 0,61 | +1,74 ± 0,66 | +1,42 ± 0,71 | (= Platz 8) |
| 16 Spieler, 7 Runden | 150 | +1,13 ± 0,51 | +1,45 ± 0,67 | +1,52 ± 0,67 | (= Platz 8) |
| 16 Spieler, 9 Runden | 150 | +0,96 ± 0,51 | +0,83 ± 0,58 | +1,40 ± 0,62 | (= Platz 8) |
| 24 Spieler, 5 Runden | 150 | +1,88 ± 0,77 | +3,26 ± 0,93 | +2,28 ± 0,96 | +1,72 ± 1,07 |
| 24 Spieler, 7 Runden | 150 | +1,29 ± 0,69 | +2,08 ± 0,88 | +1,85 ± 0,92 | +1,18 ± 1,03 |
| 24 Spieler, 9 Runden | 150 | +1,06 ± 0,58 | +2,11 ± 0,78 | +1,48 ± 0,91 | +0,66 ± 0,97 |
| 32 Spieler, 5 Runden | 150 | +2,84 ± 1,03 | +3,51 ± 1,11 | +3,78 ± 1,21 | +1,60 ± 1,20 |
| 32 Spieler, 7 Runden | 300 | +2,13 ± 0,61 | +1,96 ± 0,68 | +2,06 ± 0,84 | +1,89 ± 0,93 |
| 32 Spieler, 9 Runden | 150 | +1,39 ± 0,76 | +2,61 ± 0,93 | +1,08 ± 1,10 | +1,62 ± 1,24 |

31 von 33 Zellen (Feldgröße und Rundenzahl) gesichert schlechter, 0 gesichert besser, 2 offen; Änderung +0,66 bis +3,78 Plätze.

**Empfindlichkeit: Elo-Streuung** (Runde 1, Niederlage, 32 Spieler, 7 Runden):

| Streuung | Felder | Setzplatz 1 | Setzplatz 4 | Setzplatz 8 | Feldmitte (n/2) |
|---|---|---|---|---|---|
| σ = 50 | 150 | +3,37 ± 1,48 | +2,52 ± 1,18 | +4,78 ± 1,44 | +2,51 ± 1,35 |
| σ = 100 | 150 | +2,59 ± 0,98 | +2,80 ± 1,03 | +2,17 ± 1,32 | +3,37 ± 1,52 |
| σ = 150 | 300 | +2,13 ± 0,61 | +1,96 ± 0,68 | +2,06 ± 0,84 | +1,89 ± 0,93 |
| σ = 200 | 150 | +1,58 ± 0,83 | +1,53 ± 0,85 | +1,87 ± 1,02 | +0,26 ± 1,32 |
| σ = 300 | 150 | +1,54 ± 0,52 | +1,67 ± 0,82 | -0,02 ± 0,98 | +0,32 ± 1,10 |

17 von 20 Zellen (Elo-Streuung) gesichert schlechter, 0 gesichert besser, 3 offen; Änderung -0,02 bis +4,78 Plätze.

**Lesart der Zahlen (Deutung, nicht als Ursache gemessen).** Mit Niederlage entgeht dem Spieler in dieser Partie der Erwartungswert seiner Punkte; insgesamt sind es bei Niederlage in Runde 1 im Mittel 0,12 bis 0,53 Punkte weniger (Tabelle oben). Die Punkte liegen im Mittel niedriger in 18 von 18 Zellen mit Niederlage, in 15 von 18 Zellen mit Remis. Die Gegner werden mit Niederlage in Runde 1 im Mittel um -66 bis -12 Elo schwächer (alle Runden),
das holt im Mittel nur einen Teil dieser Punkte zurück, und der Platz wird schlechter. Mit Remis sind die Punkte in 3 von 18 Zellen nicht niedriger, die Gegner sind im Mittel nur in 3 von 6 Setzplätzen schwächer, und für die Chance auf den alleinigen Turniersieg ist bei Remis kein gesicherter Unterschied zu sehen (Setzplatz 1: 42 → 51 von 300 (nur Gambit 38, nur ehrlich 29; offen)); Platz 1 bis 3 ist bei Remis in einem Teil der Setzplätze gesichert häufiger (siehe oben). Ob ein Gambit die Streuung der Endplätze vergrößert und deshalb die Spitze erreichen kann, ist als Ursache hier nicht gemessen.
**Was die Messung belegt:** Für diese einfache Strategie ist der mittlere Endplatz mit Gambit in den gezählten Zellen schlechter, nicht besser. Das gilt für Runde 1 mit Niederlage in den gemessenen Feldern (16 bis 32 Spieler, 5 bis 9 Runden, Streuung 50 bis 300; Setzplätze 1, 4, 8 und Feldmitte) und für die Gambit-Runden 2 und 3 und die Art Remis nur im Feld der Hauptreihe (32 Spieler, 7 Runden, Streuung 150); gesichert besser ist er nur in: Setzplatz 32, Runde 1, Remis; Setzplatz 32, Runde 2, Remis; Setzplatz 32, Runde 3, Remis. **Was sie nicht belegt:** dass ein gezielter Gambit (Gegnerwahl, Zeitpunkt) oder ein Gambit unter anderen Tiebreaks oder mit Remis in den Partien nicht lohnt, und dass ein Preis an einem bestimmten Platz anders zu bewerten wäre.

## Abgrenzung

- **`schweizer-system-demo`** baut die Paarung (FIDE Dutch, Regeltext- und Matching-Modus, Abgleich mit bbpPairings) und simuliert ein Turnier. Diese Demo nutzt deren Engine als Kopie und fragt etwas anderes: was ein Spieler gewinnt, der das Regelwerk ausnutzt. Die Orakel der Engine (Abgleich mit bbpPairings) gehören dorthin; hier stehen nur der Kopier-Test und ein eigenes Orakel für das Endplatz-Modell.
- **`bracket-seeding-demo`** rechnet Setzlisten und Siegchancen im K.-o.-System (Elo, Monte Carlo); ein Gambit kommt dort nicht vor, die Setzung dort ist Voraussetzung, hier ist es der Setzplatz des Gambit-Spielers.
- **`algorithmische-kollusion-demo`** behandelt Absprachen; hier verliert ein Spieler allein, ohne Absprache. Absprachen zwischen Spielern sind ein anderes Modell.
- **`group-knockout-demo`** rechnet den letzten Spieltag einer Gruppe (Gijón); dort geht es um gleichzeitige Spiele und Wissen über das Ergebnis, nicht um das Schweizer System.

## Ehrliche Grenzen

- **Nur die einfache Strategie ist gemessen:** feste Runde (1 bis 3), feste Art (Niederlage oder Remis), keine Gegnerwahl. **Gezielte Gambits** (Zeitpunkt und Gegner nach dem Stand des Turniers) sind **nicht gemessen**; laut Suchausschnitten der Literatur (nicht im Volltext gelesen) können sie unter bestimmten Bedingungen nützen.
- **Elo-Erwartung ohne Remis.** Gewinnchance = Elo-Erwartung, Remis nur absichtlich. Echte Turniere haben viele Remis; wie der Gambit dort wirkt, ist nicht gemessen.
- **Tiebreaks.** Es zählen nur Punkte (Gleichstand gemittelt); Wertungen wie Buchholz sind nicht modelliert.
- **Bewertung nach dem mittleren Endplatz,** dazu die Chance auf Platz 1 und auf Platz 1 bis 3. Wer ein Preisgeld an einem bestimmten Platz sucht, bewertet anders; das ist nicht gemessen.
- **Alle anderen spielen ehrlich;** keine Absprachen, kein zweiter Gambit-Spieler.
- **Felder:** 16 bis 32 Spieler (gerade Zahlen), 4 bis 9 Runden, Elo normalverteilt; die Messreihen decken Feldgrößen 16, 24, 32, Rundenzahlen 5, 7, 9 und Streuungen 50 bis 300 ab. Große Open-Turniere (Hunderte Spieler) sind nicht gemessen.
- **Messunsicherheit.** 150 bis 300 Felder je Zelle; „gesichert“ ist eine Lesehilfe (zwei Standardfehler), keine Korrektur für die vielen Zellen. Gambit-Runden 2 und 3 und die Art Remis sind nur in der Hauptreihe gemessen, nicht in den Empfindlichkeitsreihen.
- **Gepaarte Zählung der Siegchance.** Das Urteil „häufiger / seltener“ für den alleinigen Turniersieg ist eine Vorzeichentest-Näherung (zwei Wurzeln aus der Zahl der abweichenden Felder), kein exakter Test, und bei wenigen Siegen (Setzplatz 4 und tiefer) fast immer „offen“.
- **Beispiel-Feld.** Ein Feld ist ein Einzelfall (siehe Verteilung oben); die Messreihen sind vorgerechnet und ändern sich nicht mit den Reglern.
- **Erklärungen als Deutung.** Dass schwächere Gegner den verlorenen Punkt nicht aufwiegen, ist die Lesart der Zahlen (Punkte und Gegnerstärke stehen in den Tabellen), keine Ursachenmessung.
- **Nicht im Browser geprüft.** Die Abbildungen sind nur mit Streamlit-AppTest geprüft (kein Docker-/Linux-Lauf, keine Browser-Ansicht).

## Bewusst nicht umgesetzt

- **Gezielte Gambits** (Gegnerwahl, Zeitpunkt nach dem Stand): nicht umgesetzt; die einfache Strategie ist der ehrliche Ausgangspunkt, die gezielte braucht ein eigenes Modell der Gegner-Auswahl.
- **Remis in den Partien** und andere **Tiebreak-Wertungen:** würden jede Zelle neu rechnen und ändern, was „Platz“ heißt.
- **Mehrere Gambit-Spieler und Absprachen:** ein anderes Modell (siehe `algorithmische-kollusion-demo`).
- **Ungerade Feldgrößen (Freilos):** der Gambit-Spieler könnte das Freilos bekommen; nicht umgesetzt, die Feldgröße ist gerade.
- **Kopie von `ss_scenario.py`:** nicht kopiert, weil die Datei die Matching-Engine (networkx) nachzieht; Elo-Erwartung und Mittelwert der Stärken sind neu geschrieben und per Test gegen die Quelle abgesichert.
- **PDF-Export, Live-Messreihen in der App:** nicht umgesetzt (die Messreihen sind vorgerechnet).

## Literatur (nicht im Volltext gelesen, nur Suchausschnitte)

- Cseh, Führlich, Lenzner: „The Swiss Gambit“, arXiv 2302.10595. Nach dem Suchausschnitt: Gambits im Schweizer System sind möglich, nützen aber nur bei hoher Vorhersagbarkeit der Ergebnisse, und der Gewinn ist begrenzt. Als Hinweis; Autoren, Titel und Nummer nach dem Suchausschnitt, nicht gegen den Volltext geprüft.

## Verifikation

- **Kern:** Ergebnisregel, Turnier, Gambit in Runde 1 und 2, Remis, Endplatz mit Gleichständen, Gegnerstärke und Prüfer gegen Handrechnung auf einem 4-Spieler-Turnier mit sicheren Siegern (`tests/test_algorithm.py`); Szenario (`tests/test_scenario.py`); Randfälle (`tests/test_edge_cases.py`); gleiches Ergebnis in zwei Prozessen mit anderem `PYTHONHASHSEED`.
- **Orakel:** `tests/test_oracle_swiss_gambit.py` zählt für 4 Spieler und 2 Runden alle Ergebnisse mit ihren Wahrscheinlichkeiten auf (exakte Brüche, Paarung der zweiten Runde von Hand abgeleitet) und vergleicht Erwartungswert und Platzverteilung mit der Simulation (1500 Zufalls-Seeds, 4,5 Standardfehler). Das Orakel ist an einer Handrechnung geprüft. Die Paarung der Kopie gegen bbpPairings wird in der `schweizer-system-demo` getestet, hier nur der Kopier-Test.
- **Kopien:** `tests/test_copies.py` vergleicht die sieben kopierten `ss_*.py` und `sga_rng.py` wörtlich mit den Quellen (überspringt sich, wenn sie fehlen).
- **Messreihen:** `tests/test_grid.py` (Aufbau, jede Zelle genau einmal, Zählungen, Probe wird nachgerechnet, ehrliche Werte unabhängig von der Variante, keine tote Variante).
- **Aussagen:** `tests/test_claims.py` (jede Tabellenzeile und Kernzahl der README aus der Messreihe), `tests/test_verdicts.py` (Schwellen und Zahlen der Verdikte).
- **Abbildungen:** `tests/test_visualization.py` (alle Achsen gesperrt, Spuren und Zahl der Punkte, Farben der Verteilung nach Vorzeichen).
- **Oberfläche:** AppTest für Standard, jedes Preset, jeden Knopf, jeden Regler an beiden Grenzen, jede Gambit-Runde und Art, jeden Setzplatz der Verteilung; Layout (Schnellstart in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben, Setzplatz folgt der Feldgröße), Footer, Laufzeit-Importe.

## Tests

133 Tests, alle grün. Laufzeit seriell 110 s (Windows, Python 3.14, Test-venv), mit `pytest -n 6` (pytest-xdist) 53 s (jeweils am 18. November 2026 gemessen, die Last des Rechners schwankt). Den größten Teil der Zeit brauchen die AppTest-Läufe (jeder Regler an beiden Grenzen, jeder Knopf: je ein frischer App-Lauf mit sieben Abbildungen). Nicht geprüft: Linux-CI (Docker), Browser-Ansicht.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Beispiel-Feld, Kernfrage, vier Experimente, Grenzen, Formeln |
| `data/gambit_grid.json` | vorgerechnete Messreihen (`tools/make_grid.py`) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt): Streamlit, Plotly |
| `sga_algorithm.py` | Kern: Turnier mit Gambit, Ergebnisregel, Endplatz, Gegnerstärke, Prüfer |
| `sga_constants.py` | Regler-Grenzen, Raster der Messreihen, Farben, Presets |
| `sga_evaluation.py` | Live-Beispiel, Zellen und Aggregation der Messreihen, Verdikte |
| `sga_layout.py` | Fester Kopf (Stylesheet) |
| `sga_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `sga_rng.py` | SplitMix64 (wörtliche Kopie der geprüften Vorlage) |
| `sga_scenario.py` | Elo-Felder, gemeinsame Zufallszahl je Partie |
| `sga_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `ss_blossom.py`, `ss_bracket.py`, `ss_colour.py`, `ss_compat.py`, `ss_engine.py`, `ss_model.py`, `ss_quality.py` | wörtliche Kopien der Engine aus der `schweizer-system-demo` (Kopf: Quelle) |
| `tools/make_grid.py` | rechnet die Messreihen vor |
| `tests/` | Handrechnung, Orakel, Kopier-Test, Messreihen, Aussagen, Verdikte, Randfälle, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Die Streamlit-Cloud-Einstellung der Python-Version ist nicht Teil dieser Demo; getestet mit Python 3.14 (lokal) und in der CI mit 3.12. <!-- lint-ok: dezimalpunkt -->

## Messreihen neu rechnen

```bash
python tools/make_grid.py --workers 8
```

Das dauert lange (beim Bau 3386 s mit 10 Prozessen) und ersetzt `data/gambit_grid.json`; danach `pytest tests/test_grid.py` und die README-Zahlen (`tests/test_claims.py`) prüfen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Wettbewerbsverzerrung: Reihenfolge und Anreize](https://sebastianhanisch.net/konzepte-wettbewerbsverzerrung.html).

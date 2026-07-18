# docs/phase0.md — Determinismus-Harness

> Gerüst, keine Lösung. Dieses Dokument sagt WAS, WARUM und in welcher REIHENFOLGE.
> Der Code wird mit Claude Code Zeile für Zeile gebaut und erklärt — nicht auf einmal generiert.

## Ziel
Ein Python-Skript (~150 Zeilen), das für 5 bekannte Aufgaben je einen Docker-Container baut, den Gold-Patch anwendet, die Testsuite ausführt — 10× pro Aufgabe — und prüft, ob das Ergebnis jedes Mal identisch ist.

**Erfolgskriterium:** 10/10 identisch bei allen 5 Aufgaben. Kein Agent, kein LLM, keine Chain.

**Warum zuerst:** Ohne Determinismus ist die gesamte spätere Krypto-Schicht wertlos, weil "anderes Ergebnis" dann kein Betrug beweist, sondern nur Rauschen. Scheitert Phase 0, ist das Konzept tot — besser in Woche 2 wissen als in Monat 8.

## Quelle der 5 Aufgaben: SWE-bench Verified
Für Phase 0 ziehen wir aus **SWE-bench Verified**. Begründung:
- Jede Instanz bringt bereits mit, was wir brauchen: ein Repo + Commit, einen Gold-Patch (`patch`), einen Testbefehl und die Liste der `FAIL_TO_PASS`-Tests.
- **Kontamination ist hier egal** — wir testen NICHT die Fähigkeit eines Agenten, sondern nur, ob die Ausführung stabil ist. Die Frische-Anforderung kommt erst ab Phase 0.5.
- Es ist die kürzeste Strecke zur einzigen Frage, die zählt: Läuft dieselbe Ausführung reproduzierbar?

## Auswahlkriterien für die 5 Tasks (determinismus-freundlich)
Claude Code soll aus dem Datensatz Kandidaten filtern, die möglichst stabil laufen, und sie mir zur Freigabe vorlegen. Bevorzugen:
1. **Reines Python**, keine kompilierten C-Extensions im Testpfad (die verhalten sich auf ARM vs. x86 anders).
2. **Keine Netzwerkzugriffe** in den Tests.
3. **Keine Zeit-/Zufalls-Abhängigkeit** (kein ungepinntes `random`, `datetime.now`, Timeouts).
4. **Kleiner Dependency-Footprint** → schnellerer, stabilerer Container-Build.
5. **Wenige `FAIL_TO_PASS`-Tests** → einfacher zu verifizieren.

Gute Kandidaten-Repos erfahrungsgemäß: `sympy`, `django` (reine ORM-Logik-Tasks), `flask`, `requests`-freie `astropy`-Tasks. Schlechte für Phase 0: alles mit `numpy`/`scipy`-Buildschritten oder Parallelität.

→ **Erste Handlung von Claude Code:** 8–10 solche Kandidaten auflisten (Instanz-ID, Repo, Anzahl FAIL_TO_PASS), damit ich 5 auswähle. Nicht blind loslegen.

## Umgebungs-Pins — Voraussetzung für Determinismus (NICHT optional)
Determinismus ist keine Eigenschaft, die man voraussetzt — man erzwingt sie. Ohne diese Kontrollen wirst du Flakiness sehen, die am Setup liegt, nicht am Task. Alle 10 Läufe müssen unter identischen, gepinnten Bedingungen laufen:

1. **`PYTHONHASHSEED=0`** setzen. Sonst variiert Dict-/Set-Reihenfolge zwischen Läufen. (Der häufigste stille Determinismus-Killer.)
2. **Image genau EINMAL bauen, dann 10× nur laufen lassen** — nicht 10× bauen. `pip`/`apt` sind selbst nicht reproduzierbar; ein Rebuild mischt Build-Rauschen ins Ergebnis. Deps im Build gepinnt (feste Versionen, kein `latest`).
3. **Test-Randomisierung und Parallelität aus:** `pytest -p no:randomly`, KEIN `-n auto` / xdist. Feste Testreihenfolge.
4. **Threads pinnen:** `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`. Multithreaded Fließkomma (numpy/BLAS) ist sonst nichtdeterministisch.
5. **`TZ=UTC`** fix. Kein Zugriff auf Wanduhr-abhängige Logik.
6. **Netz aus:** Container mit `--network none` laufen lassen.
7. **Zustands-Isolation:** pro Lauf ein frischer Container aus demselben Image (kein wiederverwendeter, mutierter Zustand).
8. **Plattform gepinnt:** `--platform linux/amd64` (siehe ARM-Abschnitt unten).

## Was "identisch" konkret heißt
Nach jedem der 10 Läufe pro Aufgabe vergleichen wir mindestens:
- **Pass/Fail-Status** jedes einzelnen `FAIL_TO_PASS`- und `PASS_TO_PASS`-Tests (nicht nur die Gesamtsumme).
- Idealerweise zusätzlich einen **Hash der normalisierten Testausgabe** (Zeitstempel, Pfade, Laufzeiten vorher rausfiltern — die dürfen variieren, das Ergebnis nicht).

Weicht auch nur ein Lauf ab → Aufgabe ist für unsere Zwecke "flaky" → wird notiert und aussortiert, nicht geflickt.

## Umgebung / ARM-Stolperstein (Entscheidung explizit treffen)
MacBook = Apple Silicon (ARM). Echte Trials laufen später auf x86-Cloud. Für Phase 0:
- Docker-Builds mit **`--platform linux/amd64`** pinnen, damit wir schon jetzt die Plattform testen, die zählt. Emulation ist langsamer — für 5 Tasks × 10 Läufe akzeptabel.
- Falls die Emulation selbst Nichtdeterminismus einbringt, ist das ein **echtes Ergebnis**, kein Bug: es sagt uns, dass die Determinismus-Garantie native x86-Runner braucht. Notieren, nicht verstecken.

## Schritt-Abfolge (so baut Claude Code, jeder Schritt einzeln + erklärt)
1. Kandidaten filtern und auflisten → ich wähle 5.
2. Für **eine** Aufgabe: Container bauen (Deps gepinnt), Gold-Patch anwenden, Tests **einmal** laufen lassen, Ergebnis parsen. (Kleinste lauffähige Einheit zuerst.)
3. Diesen einen Lauf auf **10×** erweitern, Ergebnisse vergleichen, Report ausgeben (z.B. `astropy-1234: 10/10 identisch ✓`).
4. Auf alle 5 Aufgaben verallgemeinern.
5. Sauberer Abschlussreport: pro Aufgabe 10/10 oder Abweichung + welcher Lauf abwich.

## Definition of Done
- Skript läuft mit einem Befehl durch (z.B. `python harness.py`).
- Ausgabe zeigt pro Aufgabe klar 10/10 oder die Abweichung.
- Mindestens 5 Aufgaben mit 10/10. (Aussortierte flaky Tasks durch neue Kandidaten ersetzen, bis 5 stabile stehen.)
- Ergebnis + aussortierte Tasks in CLAUDE.md Abschnitt 10 (Status) notieren.

## Was Phase 0 NICHT ist
Kein Agent, kein LLM-Call, kein Scoring, kein IRT, keine Chain, kein Leak-Scanner, kein Mutationstest. Alles das kommt später. Widersteh der Versuchung, hier schon "mehr" zu bauen.

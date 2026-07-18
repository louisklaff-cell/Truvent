# CLAUDE.md — Truvent

> Persistenter Kontext-Anker. Diese Datei wird bei jedem Start automatisch gelesen.
> Stand: Juli 2026 · Phase: Vor Phase 0 (noch kein Code) · Arbeitstitel: Truvent (Platzhalter)
> Pflege: Nach jedem Meilenstein Abschnitt "Status & nächste Aktionen" aktualisieren. Rest bleibt stabil.

## Arbeitsprinzip für dich, Claude Code (WICHTIGSTE REGEL)
Nicht "schreib mir das Projekt". Stattdessen: **kleinste lauffähige Einheit, jede Zeile erklärt, bevor du sie schreibst.** Generiere niemals ganze Skripte auf einmal. Der Gründer muss jede Zeile verstehen — er soll später einen CTO führen und einem Investor antworten können. Frage nach, statt anzunehmen.

## 1. Vision in einem Satz
Die unabhängige, nachrechenbare Prüf- und Beglaubigungsinstanz für Coding-Agenten — ein manipulationssicheres Track-Record-System, das zeigt, welchem Agenten man Code, Zugriff und Geld anvertrauen kann. Analogie: TÜV / SGS / Underwriters Laboratories für KI-Agenten. **Nicht** noch ein Leaderboard.

## 2. Getroffene Grundsatzentscheidungen
- **Zielkategorie:** nur Coding-Agenten (Erfolg objektiv messbar: Tests bestehen / PR merged). Kein Finance (Regulierung), kein Multi-Domain.
- **Technische Basis:** on-chain-natives Attestation-System. Produktversprechen ist "vertrau uns nicht, rechne nach" — unmöglich, wenn wir selbst die DB halten.
- **Token:** erst Phase 6 (18+ Monate). Zu früh = einfachster Weg, das Projekt zu killen.
- **Chain:** Solana (vorläufig, nicht endgültig). Schnell, günstig.
- **Positionierung:** Verifikationsschicht *unter* den Benchmarks, nicht "noch ein Benchmark".
- **Go-to-Market:** Private Eval-as-a-Service zuerst, Leaderboard zuletzt. Kundenbudget trägt Trial-Kosten.

## 3. Die zentrale technische Einsicht
**Der Agent muss nicht deterministisch sein. Die Bewertung muss es sein.**
Attestiert wird nicht "Agent A ist gut", sondern der Trial:
`(Task-Hash, Container-Hash, Patch-Hash, Testsuite-Hash) → (Pass/Fail, Log-Hash, Kosten)`
Das ist eine reproduzierbare Funktion, jeder kann sie nachrechnen. Ohne Determinismus ist die gesamte Krypto-Schicht wertlos — deshalb ist Phase 0 die Existenzbedingung des Projekts.

## 4. Die sechs Fehlermodi und Gegenmaßnahmen (fachlicher Kern)
1. **Kontamination** (Lösung in Trainingsdaten) → Zeitfenster: nur Tasks nach dem Cutoff aller getesteten Modelle. (Tischeinsatz, kein Burggraben.)
2. **Leakage** (.git, Changelogs, Kommentare im Container) → Hermetischer Container: kein .git, kein Netz, kein Upstream-Remote + automatischer Leak-Scan.
3a. **False Accepts** (schwache Tests winken falsche Patches durch, 8,5%) → Mutationstesting: plausible falsche Fixes erzeugen, prüfen ob Testsuite ALLE tötet; sonst Task raus.
3b. **False Rejects** (korrekte Patches fallen durch, 24%) → Gold-Patch 10× laufen lassen; alles unter 10/10 → Task raus. Zeit/Zufall/Netz gepinnt.
4. **Sättigung** (keine Trennschärfe oben) → Item Response Theory (IRT) statt "% gelöst".
5. **Selbstberichte** (Anbieter melden eigene Scores) → Wir führen aus. Scaffold+Modell als Einheit. Kosten immer mit (Pareto).
6. **Snapshot ≠ Realität** → Durability-Tracking: überlebt der PR 30 Tage?

**IRT als unterschätzter Trumpf:** modelliert pro Aufgabe Schwierigkeit + Trennschärfe, pro Agent eine latente Fähigkeit. Drei Effekte: (1) aussagekräftige Scores nahe der Decke mit Konfidenzintervallen; (2) Selbstheilung — Aufgabe mit negativer Trennschärfe ist statistisch kaputt, Benchmark findet eigene Fehler; (3) adaptive Auswahl senkt Kosten.

## 5. Die ehrliche Rolle von Krypto
Krypto macht die Bewertung nicht korrekter — die Ausführung ist die Wahrheit. Die Chain leistet nur: (1) Manipulationssicherheit (Merkle-Root on-chain, keine rückwirkende Score-Änderung); (2) Fraud Proofs statt Abstimmung (optimistische Verifikation, Stake + Challenge-Fenster); (3) Kostenverteilung ohne Runner-Vertrauen (später).

## 6. Architektur — fünf Bausteine
1. **Task-Pipeline** — Harvester (frische Commits) + QS-Gauntlet (Leak-Scan, Mutationstest, Flakiness-Screen). ~70% der Arbeit und der eigentliche Vorsprung.
2. **Hermetic Runner** — deterministische, isolierte Ausführung, bit-genau reproduzierbar.
3. **Scoring-Engine** — IRT + Kosten-Pareto + automatische Item-Health-Erkennung.
4. **Attestation-Layer** — Merkle-Root on-chain, öffentliches Verifier-CLI.
5. **Produkt** — API + Dashboard; Public Leaderboard als Marketing, private Runs als Umsatz.

## 7. Geschäftsmodell (kurz)
Leaderboard = Marketing, nicht Umsatz. Geld liegt bei Compliance-Evidenz (nur ~21% der Firmen haben reife Agent-Governance). Zielkunden in Priorität: (1) Firmen, die Coding-Agenten produktiv einsetzen und Governance-Nachweise brauchen ← Start hier; (2) Agent-Marktplätze; (3) Agenten-Hersteller (Gütesiegel). Preisannahme (unvalidiert): €1.000–3.000/Monat/Kunde. Standort EU/DE — EU AI Act als möglicher Rückenwind (mit Fachanwalt klären).

## 8. Hardware-Hinweise
MacBook Air: zum Bauen ja (Phase 0/0.5/1 reine Orchestrierung + API-Calls), zum Skalieren nein (echte Trials → x86-Cloud-VM). Zwei Stolpersteine: (1) **ARM vs. x86_64** — Apple Silicon ist ARM, Repos gehen von x86 aus; Docker emuliert, aber langsamer und teils anderes Verhalten = Determinismus-Risiko. (2) Kein Lüfter → thermisches Throttling bei langen Builds. Minimum 16GB RAM.

## 9. Roadmap
Sprachverteilung: ~80% Python, ~15% TypeScript, ~5% Rust (Rust erst ab Monat 9). Eiserne Regel: jede Phase muss ohne die nächste nützlich sein. Krypto zuletzt.

- **⭐ Phase 0 — Determinismus beweisen (Woche 1–3) ← HIER FANGEN WIR AN.** Ein Skript, ~150 Zeilen Python. 5 bekannte Aufgaben, Container bauen, Gold-Patch anwenden, Tests 10× ausführen, vergleichen. Kein Agent, kein LLM, keine Chain. **Erfolgskriterium: 10/10 identisch bei allen 5 Aufgaben.** Kosten ~0 €. Scheitert das, ist das Konzept tot — besser jetzt wissen. **Detaillierter Plan: `phase0.md`** (Aufgabenquelle, Umgebungs-Pins, Schritt-Abfolge, Definition of Done — bei Arbeit an Phase 0 immer zuerst lesen).
- **Phase 0.5 — Ersten Agenten dranhängen (Woche 3–5).** Echter Coding-Agent über API, dieselben 5 Aufgaben, 3 Läufe, Varianz messen. ~50–200 €. Nebeneffekt: erster Blogpost.
- **Phase 1 — Task-Pipeline + QS (Monat 2–4) — der Burggraben.** Harvester, Environment-Builder (Docker, Deps gepinnt), Leak-Scanner, Mutation-Tester, Flakiness-Screen. Output: ~100 saubere Tasks in SQLite.
- **Phase 2 — Scoring (Monat 4–5).** py-irt / pymc / numpyro. IRT-Modell, Kosten-Tracking, Item-Health. Output: Scores mit Konfidenzintervallen.
- **Phase 3 — Attestation (Monat 5–7).** Merkle-Root in Solana-Memo-Transaktion + Verifier-CLI (TypeScript/web3.js). Noch kein Smart Contract.
- **Phase 4 — Produkt (Monat 6–9).** FastAPI + Next.js/React Dashboard. Ziel: erster zahlender Kunde.
- **Phase 5 — Dezentralisierung (Monat 9–18).** Mehrere Runner, Fraud-Proof-Fenster, Staking. Rust/Anchor.
- **Phase 6 — Token (18+ Monate).** Nur wenn ein echtes Netzwerk existiert.

## 10. Status & nächste Aktionen (HIER PFLEGEN)
**Aktueller Stand (18.07.2026):** Phase 0 abgeschlossen. Erfolgskriterium erfüllt: 10/10 identisch bei allen 5 Aufgaben (`django__django-10880`, `psf__requests-1142`, `pylint-dev__pylint-4661`, `pytest-dev__pytest-10051`, `sympy__sympy-11618`, aus SWE-bench Verified), reproduzierbar mit einem Befehl (`python scripts/harness.py`). Details, Kandidatenauswahl und Umgebungs-Pins in `phase0.md`. Keine Aufgaben mussten wegen Flakiness aussortiert werden -- alle 5 ursprünglich gewählten Kandidaten bestanden direkt.

Gelernt dabei (relevant für Phase 1, den Harvester):
- Jedes Repo hat einen eigenen Testrunner und ein eigenes Ausgabeformat (Django: `runtests.py`, sympy: `bin/test`, Rest: `pytest`) -- die Task-Pipeline muss das pro Repo kapseln, nicht einheitlich annehmen.
- Ein offizielles SWE-bench-Image hatte eine fehlende Abhängigkeit (`pylint-dev__pylint-4661`, `appdirs`) -- musste einmalig mit Netzzugriff gefixt und als eigenes Image commited werden. Zeigt: auch "verifizierte" Referenz-Images können environment-seitig lückenhaft sein, eigener Leak-/Health-Scan in Phase 1 bleibt nötig.
- sympy nennt in FAIL_TO_PASS/PASS_TO_PASS nur nackte Testnamen ohne Dateibezug -- Datei wurde aus dem Diff-Header von `test_patch` abgeleitet.

Nächster Schritt: Phase 0.5 (ersten echten Coding-Agenten über API auf dieselben 5 Aufgaben ansetzen, Varianz messen).

Offene Fragen:
- [x] Python + Docker auf dem MacBook prüfen -- erledigt in Phase 0: Docker mit `--platform linux/amd64`-Emulation lief stabil und deterministisch (10/10) über alle 5 Aufgaben, kein Nichtdeterminismus durch Emulation beobachtet
- [ ] EU AI Act: Konformitätsbewertungs-Rückenwind? (Fachanwalt)
- [ ] Lizenzfrage SWE-bench Verified: Datensatz selbst hat kein explizites Lizenz-Tag, enthält Diffs aus Repos mit unterschiedlichen Lizenzen (u.a. GPL-2.0 bei pylint). Für Phase 0 (rein intern, keine Weitergabe) unkritisch. Vor kommerzieller Eval-as-a-Service-Nutzung (Phase 1+) mit Fachanwalt klären — löst sich langfristig ohnehin durch eigenen Harvester (Kontamination, siehe Fehlermodus 1)
- [ ] Chain final: Solana bestätigen oder Alternativen prüfen
- [ ] Erste 5 Test-Aufgaben: aus welcher Quelle?
- [ ] Erster Kundenkandidat für private Eval-as-a-Service?
- [ ] Preisannahme €1–3k/Monat validieren

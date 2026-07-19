# CLAUDE.md — Truvent

> Persistenter Kontext-Anker. Diese Datei wird bei jedem Start automatisch gelesen.
> Stand: Juli 2026 · Phase: Vor Phase 0 (noch kein Code) · Arbeitstitel: Truvent (Platzhalter)
> Pflege: Nach jedem Meilenstein Abschnitt "Status & nächste Aktionen" aktualisieren. Rest bleibt stabil.

## Arbeitsprinzip für dich, Claude Code (WICHTIGSTE REGEL)
Nicht "schreib mir das Projekt". Stattdessen: **kleinste lauffähige Einheit, jede Zeile erklärt, bevor du sie schreibst.** Generiere niemals ganze Skripte auf einmal. Der Gründer muss jede Zeile verstehen — er soll später einen CTO führen und einem Investor antworten können. Frage nach, statt anzunehmen.

**Geschäftlich schonungslos ehrlich sein.** Nicht beschönigen, keine Wettbewerbsvorteile/Alleinstellungsmerkmale behaupten, die nicht sauber belegt sind, keine Cheerleading-Antworten auf strategische Fragen. Wenn eine Einschätzung zu optimistisch war, das aktiv selbst korrigieren, sobald es auffällt — auch unaufgefordert, auch wenn's unbequem ist. Der Gründer trifft Entscheidungen mit echtem Geld und echter Zeit; er braucht eine kalibrierte Einschätzung, keine Bestätigung. (Grund: Am 18.07.2026 hat Claude eine Formulierung zu großzügig ausgelegt — "das hast du heute als Erster gebaut" impliziert, obwohl die Technik selbst bei METR & Co. längst Praxis ist. Der Gründer hat das selbst bemerkt und nachgefragt. Nicht wieder passieren lassen.)

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

- **⭐ Phase 0 — Determinismus beweisen (Woche 1–3) — ERLEDIGT (18.07.2026).** Ein Skript, ~150 Zeilen Python. 5 bekannte Aufgaben, Container bauen, Gold-Patch anwenden, Tests 10× ausführen, vergleichen. Kein Agent, kein LLM, keine Chain. **Erfolgskriterium: 10/10 identisch bei allen 5 Aufgaben.** Kosten ~0 €. **Detaillierter Plan: `phase0.md`**. Ergebnis + Code: `github.com/louisklaff-cell/Truvent` (privat).
- **🔦 Lackmustests (vor Phase 0.5/1 vorgeschaltet, ~30–100€, wenige Wochen) ← HIER STEHEN WIR JETZT.** Zwei billige Vorab-Checks, ob sich der große Aufwand von Phase 0.5/1 überhaupt lohnt — Ergebnis aus einer Wettbewerbs-/Nachfragerecherche vom 18.07.2026 (Details in Claude-Memory "truvent-competitive-landscape"):
  1. **QS-Gauntlet gegen bestehende Tasks** — Mutationstest + Flakiness-Screen + Leak-Scan auf schon existierenden SWE-bench-Aufgaben anwenden. Testfrage: Findet unser QS-Handwerk nachweisbar mehr kaputte Aufgaben, als ein grobes Konkurrenz-Skript finden würde? Ist eher ein Urteilsaufruf als ein sauberes Experiment — kein 10/10-artiges Ergebnis zu erwarten.
  2. **Zahlender Design-Partner** — aus 10 echten PRs eines einzelnen Kunden deterministische Eval-Tasks bauen, ab dem ersten Kunden Geld verlangen (Pilot). Testfrage: Wie lange dauert das Onboarding pro Kunde (kurz = leicht kopierbares Feature, lang = echter Burggraben), und zahlt überhaupt jemand?
  Beide Tests ersetzen Phase 0.5/1 nicht, sondern gehen ihnen als schlanke Vorabprüfung voraus — bestehen sie, wird mit mehr Vertrauen in Phase 0.5/1 investiert; fallen sie durch, eher Andocken an bestehende Anbieter statt eigene Firma.
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

Zwischenzeitlich: Wettbewerbs-/Nachfragerecherche durchgeführt (18.07.2026, Details in Claude-Memory "truvent-competitive-landscape"). Kernbefund: Nachfrage real und belegt, aber Krypto-/On-Chain-Schicht hat kein Nachfragesignal und ist nachbaubar — der eigentliche Burggraben liegt in der QS-Gauntlet-Tiefe + kundenspezifischem Task-Manufacturing, nicht in der Chain. Naher Wettbewerber: AIUC (TÜV+Versicherung für KI-Agenten, aber nicht Coding-spezifisch, nicht deterministik-getrieben).

**Lackmustest 1 (QS-Gauntlet gegen bestehende Tasks) — Zwischenergebnis (18.07.2026):** Leak-Scan (Git-Historie + verdächtige Kommentare) und Mutationstesting gegen alle 5 Phase-0-Aufgaben gebaut und ausgeführt (`scripts/leak_scan.py`, `scripts/mutation_test.py`). Kein Git-Historien-Leck bei keiner Aufgabe. Von 10 handgebauten Mutanten (2 pro Aufgabe, je ein leichter + ein schwererer) rutschen **3 komplett durch die volle Testsuite (FALSE_ACCEPT)**: requests-1142 (Content-Length bei DELETE ungetestet), pylint-4661 (Migrationswarnung ungetestet), sympy-11618 (distance()-Fix nur in einer Aufrufrichtung getestet) — bei bewusst plausiblen, "fast richtigen" Fixes. Erster konkreter Beleg, dass unser QS-Handwerk echte Lücken findet, die die reine 10/10-Determinismus-Prüfung aus Phase 0 nicht aufdeckt. Unterwegs zwei eigene Bugs im Test-Harness gefunden und behoben (Label-Format-Mismatch, korrupte handgetippte Patches).

**Lackmustest 1 — naiver Vergleich, vorläufiges Verdikt (18.07.2026):** Fünf rein mechanische Mutationen (Bedingung negieren, Tupel-Element entfernen, Anweisung löschen, max↔min tauschen), blind ohne vorherige Testlektüre erzeugt. Ergebnis: nur 1/5 (20%) rutscht durch — exakt dieselbe Lücke, die auch unser gezielter Mutant fand (pylint, praktisch jede Änderung dort bleibt unentdeckt). Die anderen beiden echten Funde (requests DELETE, sympy Aufrufrichtung) wurden von der blinden Mutation NICHT gefunden. Naiv: 1/5 (20%) unentdeckt. Gezielt (unsere "schweren" Mutanten): 3/5 (60%) unentdeckt. **Vorläufiges Fazit: unser QS-Handwerk findet auf dieser kleinen Stichprobe mehr als ein blindes Skript — 2 von 3 echten Funden brauchten gezieltes Lesen der Testsuite, nicht nur Mechanik.** Einschränkung: Stichprobe sehr klein (5 Aufgaben, 1 naiver Mutant/Aufgabe) — kein belastbarer statistischer Beweis, aber ein echtes, nicht wegdiskutierbares Signal in die richtige Richtung.

Nächster Schritt: Lackmustest 1 gilt als abgeschlossen genug für eine erste Einschätzung. Weiter mit Lackmustest 2 (zahlender Design-Partner) — Entscheidung mit Gründer, wen ansprechen und wie das Angebot aussieht.

Offene Fragen:
- [x] Python + Docker auf dem MacBook prüfen -- erledigt in Phase 0: Docker mit `--platform linux/amd64`-Emulation lief stabil und deterministisch (10/10) über alle 5 Aufgaben, kein Nichtdeterminismus durch Emulation beobachtet
- [ ] EU AI Act: Konformitätsbewertungs-Rückenwind? (Fachanwalt)
- [ ] Lizenzfrage SWE-bench Verified: Datensatz selbst hat kein explizites Lizenz-Tag, enthält Diffs aus Repos mit unterschiedlichen Lizenzen (u.a. GPL-2.0 bei pylint). Für Phase 0 (rein intern, keine Weitergabe) unkritisch. Vor kommerzieller Eval-as-a-Service-Nutzung (Phase 1+) mit Fachanwalt klären — löst sich langfristig ohnehin durch eigenen Harvester (Kontamination, siehe Fehlermodus 1)
- [ ] Chain final: Solana bestätigen oder Alternativen prüfen
- [ ] Erste 5 Test-Aufgaben: aus welcher Quelle?
- [ ] Erster Kundenkandidat für private Eval-as-a-Service?
- [ ] Preisannahme €1–3k/Monat validieren

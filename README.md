# Truvent — Code-Übersicht

> Für die Vision, Geschäftsentscheidungen und den aktuellen Projektstand: siehe `CLAUDE.md`.
> Für den detaillierten Phase-0-Plan: siehe `phase0.md`.
> Für die Lackmustest-2-Vorbereitung (Kundenansprache): siehe `docs/lackmustest2_prep.md`.

Dieses Dokument erklärt nur den **Code selbst** — wie die Skripte zusammenhängen und wie man sie ausführt.

## Voraussetzungen

- Python-Umgebung in `.venv/` (`python3 -m venv .venv`, dann `.venv/bin/pip install -r` entfällt — Pakete wurden einzeln installiert: `requests`, `anthropic`, `python-dotenv`)
- Docker Desktop, läuft mit `--platform linux/amd64`-Emulation (auch auf Apple Silicon)
- Für Agenten-Läufe: `.env`-Datei im Projekt-Root mit `ANTHROPIC_API_KEY=...` (nicht committen, steht in `.gitignore`)

## Architektur — wie die Skripte zusammenhängen

```
run_once.py          ← Kern: EINE Aufgabe EINMAL ausführen
  ├── check_determinism.py   ← denselben Task 10x wiederholen, Fingerabdruck vergleichen
  ├── mutation_test.py       ← statt Gold-Patch einen falschen Patch einsetzen
  │     └── run_agent.py     ← statt handgebautem Mutant: echten KI-Output einsetzen
  │           └── run_agent_harness.py   ← alle Aufgaben x Modelle x Wiederholungen
  └── harness.py              ← alle 5 Aufgaben, jeweils 10x, Abschlussreport

leak_scan.py          ← unabhängig: Git-Historie + Kommentare auf Hinweise prüfen
list_repos.py, list_candidates.py, explore_schema.py   ← einmalige Recherche-Skripte (Kandidatenauswahl in Phase 0)
```

**Das Grundprinzip von `run_once.py`:** Für eine `instance_id` (z. B. `django__django-10880`) wird ein frischer, isolierter Docker-Container gestartet (`--network none`, `PYTHONHASHSEED=0`, `--platform linux/amd64`, gepinnte Threads — siehe `phase0.md` für die Begründung jedes einzelnen Pins), ein Patch angewendet, die Testsuite ausgeführt, das Ergebnis geparst. Jedes Repo (Django, sympy, ...) hat einen eigenen Testrunner und ein eigenes Ausgabeformat — das kapselt `REPO_CONFIGS` in `run_once.py`.

Alle anderen Skripte bauen darauf auf, indem sie **welcher Patch angewendet wird** austauschen:

| Skript | Ersetzt `gold.patch` durch | Zweck |
|---|---|---|
| `harness.py` | (nichts, nutzt den echten Gold Patch) | Beweist: ist die Messung selbst deterministisch? |
| `mutation_test.py` | einen handgebauten, absichtlich falschen Patch | Ist die Testsuite streng genug (Fehlermodus 3a)? |
| `run_agent.py` | einen von Claude live generierten Patch | Verarbeitet das System echten, unvorhersehbaren KI-Output? |

## Verzeichnisstruktur pro Aufgabe (`tasks/<instance_id>/`)

- `meta.json` — Repo, FAIL_TO_PASS/PASS_TO_PASS-Testnamen, Version
- `gold.patch` — der echte, historisch gemergte Fix
- `test.patch` — fügt den/die neuen Test(s) hinzu
- `problem_statement.txt` — die ursprüngliche Bug-Beschreibung
- `mutants/` — handgebaute falsche Patches (Lackmustest 1)
- `mutants_naive/` — mechanisch/blind erzeugte Vergleichs-Mutanten
- `agent_patches/` — von echten KI-Modellen generierte Patches (Mini-Phase-0.5)

## `docker-fixes/`

Manche offiziellen SWE-bench-Images haben Lücken (z. B. fehlende Abhängigkeiten). Statt das nur einmalig manuell im laufenden Container zu reparieren (`docker commit`, nur auf diesem einen Rechner reproduzierbar), liegt hier pro betroffener Aufgabe ein Dockerfile, das den Fix nachvollziehbar und auf jeder Maschine neu baubar macht. Nach dem Bauen den neuen Digest in `scripts/run_once.py` → `IMAGE_DIGESTS` eintragen.

## Typische Befehle

```bash
# Eine Aufgabe einmal pruefen
.venv/bin/python3 scripts/run_once.py django__django-10880

# Eine Aufgabe 10x wiederholen (Determinismus-Check)
.venv/bin/python3 scripts/check_determinism.py django__django-10880

# Alle 5 Aufgaben, voller Phase-0-Report
.venv/bin/python3 scripts/harness.py

# Einen Mutanten gegen eine Aufgabe testen
.venv/bin/python3 scripts/mutation_test.py django__django-10880 tasks/django__django-10880/mutants/mutant_1_space_before.patch

# Leak-Scan fuer eine Aufgabe
.venv/bin/python3 scripts/leak_scan.py django__django-10880

# Einen einzelnen Agentenlauf (kostet echtes API-Geld!)
.venv/bin/python3 scripts/run_agent.py psf__requests-1142 claude-sonnet-5 1

# Vollen Agenten-Testlauf, alle Aufgaben x Modelle x Wiederholungen (kostet echtes API-Geld!)
.venv/bin/python3 scripts/run_agent_harness.py
```

Alle Befehle aus dem Projekt-Root ausführen (nicht aus `scripts/`), sonst stimmen die relativen Pfade zu `tasks/` nicht.

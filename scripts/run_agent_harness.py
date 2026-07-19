"""Volle Mini-Phase-0.5: alle 5 Aufgaben, 3 Wiederholungen, 3 Modelle.

45 echte API-Aufrufe insgesamt. Testet drei Dinge gleichzeitig:
(1) verarbeitet unser Harness echten, unvorhersehbaren KI-Output
    korrekt, statt nur unsere eigenen sauberen Patches?
(2) wie stark schwankt ein Agent bei mehreren Versuchen derselben
    Aufgabe -- und unterscheidet sich das zwischen den Modellen?
(3) erkennt unser System auch ECHTE (nicht von uns gebaute) falsche
    Versuche -- Haiku als schwaecheres Modell soll das wahrscheinlicher
    machen, ohne dass wir Fehler kuenstlich erzwingen muessen.
"""
from collections import Counter
from pathlib import Path

from run_agent import TASKS_DIR, run_agent_attempt

INSTANCES = [
    "django__django-10880",
    "psf__requests-1142",
    "pylint-dev__pylint-4661",
    "pytest-dev__pytest-10051",
    "sympy__sympy-11618",
]
MODELS = ["claude-sonnet-5", "claude-opus-4-8", "claude-haiku-4-5-20251001"]
RUNS_PER_MODEL = 3

if __name__ == "__main__":
    results = []
    for instance_id in INSTANCES:
        out_dir = TASKS_DIR / instance_id / "agent_patches"
        out_dir.mkdir(exist_ok=True)
        for model in MODELS:
            for run_number in range(1, RUNS_PER_MODEL + 1):
                print(f"\n=== {instance_id} / {model} / Lauf {run_number} ===")
                verdict, detail, patch_path = run_agent_attempt(
                    instance_id, model, str(run_number), out_dir
                )
                print(f"  {verdict}")
                results.append((instance_id, model, run_number, verdict))

    print("\n=== Abschlussreport ===")
    for instance_id, model, run_number, verdict in results:
        print(f"  {instance_id} / {model} / Lauf {run_number}: {verdict}")

    print("\n=== Zusammenfassung pro Aufgabe x Modell ===")
    for instance_id in INSTANCES:
        for model in MODELS:
            verdicts = [v for i, m, r, v in results if i == instance_id and m == model]
            tally = Counter(verdicts)
            print(f"  {instance_id} / {model}: {dict(tally)}")

    print("\n=== Robustheits-Check (Testfrage 1) ===")
    invalid = [r for r in results if r[3] == "PATCH_UNGUELTIG"]
    print(f"  {len(invalid)} von {len(results)} Patches liessen sich nicht anwenden.")

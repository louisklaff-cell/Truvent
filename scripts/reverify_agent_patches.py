"""Prueft alle bereits gespeicherten Agent-Patches erneut mit der
korrigierten mutation_test.py-Logik (Marker statt Text-Matching) --
ohne neue API-Aufrufe, nur die alten Dateien aus agent_patches/.

Laeuft parallel (reine Docker-Verifikation, keine API-Aufruf-Limits
zu beachten -- siehe check_determinism.py fuer die Sicherheitsbegruendung).
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from mutation_test import check_mutant
from run_agent import VERDICT_LABELS

TASKS_DIR = Path(__file__).parent.parent / "tasks"
MAX_PARALLEL = 10

INSTANCES = [
    "django__django-10880",
    "psf__requests-1142",
    "pylint-dev__pylint-4661",
    "pytest-dev__pytest-10051",
    "sympy__sympy-11618",
]


def _verify_one(instance_id, patch_path):
    raw_verdict, detail = check_mutant(instance_id, patch_path)
    return instance_id, patch_path, VERDICT_LABELS[raw_verdict]


if __name__ == "__main__":
    jobs = [
        (instance_id, patch_path)
        for instance_id in INSTANCES
        for patch_path in sorted((TASKS_DIR / instance_id / "agent_patches").glob("*.patch"))
    ]

    tally = Counter()
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as ex:
        futures = [ex.submit(_verify_one, i, p) for i, p in jobs]
        for future in futures:
            instance_id, patch_path, verdict = future.result()
            tally[verdict] += 1
            print(f"{instance_id} / {patch_path.name}: {verdict}")

    print("\n=== Korrigierte Gesamtzahlen ===")
    for verdict, count in tally.items():
        print(f"  {verdict}: {count}")

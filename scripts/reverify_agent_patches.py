"""Prueft alle bereits gespeicherten Agent-Patches erneut mit der
korrigierten mutation_test.py-Logik (Marker statt Text-Matching) --
ohne neue API-Aufrufe, nur die alten Dateien aus agent_patches/.
"""
from collections import Counter
from pathlib import Path

from mutation_test import check_mutant
from run_agent import VERDICT_LABELS

TASKS_DIR = Path(__file__).parent.parent / "tasks"

INSTANCES = [
    "django__django-10880",
    "psf__requests-1142",
    "pylint-dev__pylint-4661",
    "pytest-dev__pytest-10051",
    "sympy__sympy-11618",
]

if __name__ == "__main__":
    tally = Counter()
    for instance_id in INSTANCES:
        patch_dir = TASKS_DIR / instance_id / "agent_patches"
        for patch_path in sorted(patch_dir.glob("*.patch")):
            raw_verdict, detail = check_mutant(instance_id, patch_path)
            verdict = VERDICT_LABELS[raw_verdict]
            tally[verdict] += 1
            print(f"{instance_id} / {patch_path.name}: {verdict}")

    print("\n=== Korrigierte Gesamtzahlen ===")
    for verdict, count in tally.items():
        print(f"  {verdict}: {count}")

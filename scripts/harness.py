"""Phase 0, Schritt 5: ein Befehl, alle 5 Aufgaben, sauberer Abschlussreport."""
from check_determinism import check_determinism

INSTANCES = [
    "django__django-10880",
    "psf__requests-1142",
    "pylint-dev__pylint-4661",
    "pytest-dev__pytest-10051",
    "sympy__sympy-11618",
]

if __name__ == "__main__":
    results = {}
    for instance_id in INSTANCES:
        print(f"\n=== {instance_id} ===")
        results[instance_id] = check_determinism(instance_id)

    print("\n=== Abschlussreport ===")
    all_ok = True
    for instance_id, ok in results.items():
        status = "10/10 identisch ✓" if ok else "ABWEICHUNG ✗"
        print(f"  {instance_id}: {status}")
        all_ok = all_ok and ok

    print(f"\nErfolgskriterium (10/10 bei allen 5 Aufgaben): {'ERFUELLT' if all_ok else 'NICHT ERFUELLT'}")

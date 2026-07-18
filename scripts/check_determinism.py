"""Phase 0, Schritt 3: einen Task 10x laufen lassen, Ergebnisse vergleichen."""
import hashlib
import sys

from run_once import load_meta, parse_results, run_once, to_dotted_labels

N_RUNS = 10


def fingerprint(results):
    """Hash aus den sortierten (Testname, Status)-Paaren -- normalisiert,
    damit Laufzeiten/Zeitstempel im Rohtext keine Rolle spielen."""
    normalized = sorted(results.items())
    text = repr(normalized).encode()
    return hashlib.sha256(text).hexdigest()[:12]


def check_determinism(instance_id, n_runs=N_RUNS):
    meta = load_meta(instance_id)
    expected_labels = set(to_dotted_labels(meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"]))

    fingerprints = []
    for i in range(1, n_runs + 1):
        output, _ = run_once(instance_id)
        results = parse_results(output)
        fp = fingerprint(results)
        fingerprints.append(fp)

        missing = expected_labels - results.keys()
        failed = {l for l in expected_labels if results.get(l) != "ok"} - missing
        status = "ok" if not missing and not failed else "ABWEICHUNG"
        print(f"  Lauf {i:2d}/{n_runs}: fingerprint={fp}  {status}")

    unique = set(fingerprints)
    if len(unique) == 1:
        print(f"{instance_id}: {n_runs}/{n_runs} identisch ✓  (fingerprint={fingerprints[0]})")
        return True
    else:
        print(f"{instance_id}: NICHT deterministisch -- {len(unique)} verschiedene Ergebnisse unter {n_runs} Laeufen")
        for fp in unique:
            runs_with_fp = [i + 1 for i, f in enumerate(fingerprints) if f == fp]
            print(f"  fingerprint={fp}: Laeufe {runs_with_fp}")
        return False


if __name__ == "__main__":
    instance_id = sys.argv[1] if len(sys.argv) > 1 else "django__django-10880"
    ok = check_determinism(instance_id)
    sys.exit(0 if ok else 1)

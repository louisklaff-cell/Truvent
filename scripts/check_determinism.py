"""Phase 0, Schritt 3: einen Task 10x laufen lassen, Ergebnisse vergleichen.

Laeuft parallel statt sequenziell -- sicher, weil jeder Lauf einen
frischen, isolierten Container mit eindeutigem Namen und gepinnten
Threads bekommt (siehe run_once.py). Empirisch verifiziert (20.07.2026):
10 parallele Laeufe liefern exakt dieselben Ergebnisse wie sequenziell,
nur ~10x schneller (2,6s statt ~26s). Die Reihenfolge der Laeufe spielt
fuer unabhaengige, isolierte Prozesse keine Rolle -- Parallelitaet
aendert nichts an der Aussagekraft der Determinismus-Pruefung selbst.
"""
import hashlib
import sys
from concurrent.futures import ThreadPoolExecutor

from run_once import expected_labels, load_meta, parse_results, run_once

N_RUNS = 10
MAX_PARALLEL = 10  # Obergrenze, um den Host nicht zu ueberlasten


def fingerprint(results):
    """Hash aus den sortierten (Testname, Status)-Paaren -- normalisiert,
    damit Laufzeiten/Zeitstempel im Rohtext keine Rolle spielen."""
    normalized = sorted(results.items())
    text = repr(normalized).encode()
    return hashlib.sha256(text).hexdigest()[:12]


def _single_run(instance_id, meta):
    output, _ = run_once(instance_id)
    results = parse_results(output, meta)
    return fingerprint(results), results


def check_determinism(instance_id, n_runs=N_RUNS, max_parallel=MAX_PARALLEL):
    meta = load_meta(instance_id)
    expected = set(expected_labels(meta))

    with ThreadPoolExecutor(max_workers=min(n_runs, max_parallel)) as ex:
        futures = [ex.submit(_single_run, instance_id, meta) for _ in range(n_runs)]
        run_data = [f.result() for f in futures]

    fingerprints = []
    all_runs_ok = True
    for i, (fp, results) in enumerate(run_data, start=1):
        fingerprints.append(fp)
        missing = expected - results.keys()
        failed = {l for l in expected if results.get(l) != "ok"} - missing
        run_ok = not missing and not failed
        all_runs_ok = all_runs_ok and run_ok
        status = "ok" if run_ok else "ABWEICHUNG"
        print(f"  Lauf {i:2d}/{n_runs}: fingerprint={fp}  {status}")

    # WICHTIG: "identische Fingerprints" allein reicht nicht. Wenn alle 10
    # Laeufe auf dieselbe Weise scheitern (Timeout, Absturz, fehlendes
    # Image -> leeres Parse-Ergebnis), waeren die Fingerprints ebenfalls
    # identisch -- das darf NICHT als "10/10 identisch (bestanden)" gelten.
    # Deterministisch UND korrekt sind zwei getrennte Bedingungen, beide
    # muessen erfuellt sein. (Fund eines unabhaengigen Audits am 21.07.2026 --
    # vier eigene Audit-Runden zuvor hatten genau das uebersehen.)
    unique = set(fingerprints)
    deterministic = len(unique) == 1

    if deterministic and all_runs_ok:
        print(f"{instance_id}: {n_runs}/{n_runs} identisch ✓  (fingerprint={fingerprints[0]})")
        return True
    elif deterministic and not all_runs_ok:
        print(
            f"{instance_id}: {n_runs}/{n_runs} IDENTISCH, ABER ALLE LAEUFE FEHLGESCHLAGEN "
            f"-- fingerprint={fingerprints[0]} steht fuer keinen erfolgreichen Zustand "
            f"(z.B. Timeout, Absturz oder fehlendes Image bei jedem Lauf)"
        )
        return False
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

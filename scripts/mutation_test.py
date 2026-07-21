"""Lackmustest 1, Teil 2: Mutationstesting.

Wendet statt des echten Gold-Patches einen plausiblen FALSCHEN Patch
(Mutant) an und prueft: faengt die Testsuite das ab (FAIL_TO_PASS
bleibt FAIL/fehlt), oder faellt sie darauf herein (FAIL_TO_PASS wird
faelschlich "ok")? Letzteres waere Fehlermodus 3a aus CLAUDE.md --
eine zu schwache Testsuite, die auch falsche Fixes durchwinkt.

Der Mutant nimmt technisch den Platz von gold.patch ein: wir bauen
ein temporaeres Verzeichnis mit test.patch (unveraendert) + Mutant
(als gold.patch benannt) und mounten das statt des echten Task-Ordners.
"""
import shutil
import sys
import tempfile
from pathlib import Path

from run_once import (
    _CANARY_FILE,
    _CANARY_MOUNT_PATH,
    _CANARY_SUPPORTED_REPOS,
    _files_from_patch,
    _test_file_from_patch,
    canary_violation,
    expected_labels,
    forbidden_infra_files,
    image_name,
    load_meta,
    parse_results,
    render_inner_cmd,
    run_docker_with_cleanup,
    touched_files,
)

TASKS_DIR = Path(__file__).parent.parent / "tasks"


def run_with_mutant(instance_id, mutant_path):
    meta = load_meta(instance_id)
    real_task_dir = TASKS_DIR / instance_id
    labels = expected_labels(meta)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        shutil.copy(real_task_dir / "test.patch", tmp_path / "test.patch")
        shutil.copy(mutant_path, tmp_path / "gold.patch")

        test_file = _test_file_from_patch(tmp_path)
        restore_files = _files_from_patch(tmp_path / "test.patch")
        inner_cmd = render_inner_cmd(meta, labels, test_file, restore_files)

        docker_cmd = [
            "docker", "run", "--rm",
            "--platform", "linux/amd64",
            "--network", "none",
            "-e", "PYTHONHASHSEED=0",
            "-e", "PYTHONIOENCODING=UTF-8",
            "-e", "LC_ALL=C.UTF-8",
            "-e", "LANG=C.UTF-8",
            "-e", "TZ=UTC",
            "-e", "OMP_NUM_THREADS=1",
            "-e", "OPENBLAS_NUM_THREADS=1",
            "-e", "MKL_NUM_THREADS=1",
            "-v", f"{tmp_path.resolve()}:/patches:ro",
        ]
        if meta["repo"] in _CANARY_SUPPORTED_REPOS:
            docker_cmd += ["-v", f"{_CANARY_FILE.resolve()}:{_CANARY_MOUNT_PATH}:ro"]
        docker_cmd += [
            image_name(instance_id),
            "bash", "-c", inner_cmd,
        ]
        output = run_docker_with_cleanup(docker_cmd, timeout=300)
        return output, meta


def check_mutant(instance_id, mutant_path):
    output, meta = run_with_mutant(instance_id, mutant_path)

    # Timeout ist ein eigener Zustand -- weder "Patch ungueltig" noch ein
    # Testergebnis. Getrennt behandeln statt faelschlich als UNGUELTIG
    # zu werten (der Patch koennte gueltig gewesen sein, die Tests haben
    # nur zu lange gebraucht).
    if output.startswith("TRUVENT_TIMEOUT"):
        return "TIMEOUT", output

    # Wenn der Marker TRUVENT_APPLY_OK fehlt, ist das Patchen fehlgeschlagen --
    # egal mit welcher Fehlermeldung. Robuster als nach bekannten Fehler-
    # texten zu suchen, die je nach git-Version/Fehlerart variieren koennen.
    if "TRUVENT_APPLY_OK" not in output:
        return "MUTANT_UNGUELTIG", output

    # Sperrlisten-Pruefung auf Dateisystem-Wahrheit (touched_files()), NICHT
    # auf dem rohen Diff-Text von gold.patch -- siehe forbidden_infra_files()-
    # Kommentar in run_once.py fuer den Grund (Diff-Format-Umgehungen eines
    # unabhaengigen Audits, 21.07.2026). Fehlen die Marker trotz vorhandenem
    # TRUVENT_APPLY_OK (sollte nicht passieren, da beide im selben "&&"-
    # Befehlsstrang stehen), sicherheitshalber ablehnen statt anzunehmen,
    # es sei nichts Verbotenes dabei.
    touched = touched_files(output)
    if touched is None:
        return "MUTANT_UNGUELTIG", "TRUVENT_APPLY_OK vorhanden, aber Datei-Marker fehlen -- sicherheitshalber abgelehnt"

    real_gold_files = _files_from_patch(TASKS_DIR / instance_id / "gold.patch")
    forbidden = forbidden_infra_files(touched, exempt=real_gold_files)
    if forbidden:
        return "FORBIDDEN_FILES", f"Kandidaten-Patch beruehrt Test-Infrastruktur: {forbidden}"

    actual = parse_results(output, meta)

    # Kanarienvogel-Integritaet zuerst pruefen -- eine Verletzung bedeutet
    # (undifferenzierte) Manipulation der Testauswertung selbst, ist also
    # kein normales "Test bestanden/fehlgeschlagen"-Ergebnis mehr und
    # bekommt einen eigenen Verdikt-Zustand statt in KORREKT_ABGELEHNT/
    # FALSE_ACCEPT gemischt zu werden.
    violation = canary_violation(actual, meta["repo"])
    if violation:
        return "KANARIENVOGEL_VERLETZT", violation

    all_expected = expected_labels(meta)

    # "Getoetet" heisst: IRGENDEIN Test aus der GESAMTEN Suite schlaegt an
    # (nicht "ok") -- egal ob FAIL_TO_PASS oder PASS_TO_PASS. Erst wenn
    # WIRKLICH ALLES gruen bleibt, hat der Mutant die Suite komplett
    # ueberlebt -- das ist der eigentliche False-Accept-Fall aus CLAUDE.md.
    killed_by = [t for t in all_expected if actual.get(t) != "ok"]
    if killed_by:
        return "KORREKT_ABGELEHNT", killed_by
    return "FALSE_ACCEPT", None


if __name__ == "__main__":
    instance_id = sys.argv[1]
    mutant_path = Path(sys.argv[2])
    verdict, detail = check_mutant(instance_id, mutant_path)
    print(f"{instance_id} / {mutant_path.name}: {verdict}")
    if detail:
        print(f"  {detail}")

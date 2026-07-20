"""Phase 0, Schritt 2/4: eine Aufgabe, ein Lauf, Ergebnis parsen.

Jedes Repo hat seinen eigenen Testrunner und sein eigenes Ausgabeformat.
REPO_CONFIGS kapselt das pro Repo: wie die Testliste fuer die Kommandozeile
gebaut wird, welcher Shell-Befehl im Container laeuft, und wie die
Ausgabe zurueck in {test_id: status} geparst wird.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TASKS_DIR = Path(__file__).parent.parent / "tasks"

# Django: "test_count (aggregation.tests.AggregateTestCase) ... ok"
DJANGO_RESULT_LINE = re.compile(r"^(.+?) \((.+?)\) \.\.\. (ok|FAIL|ERROR)$", re.MULTILINE)
# pytest -v: "test_requests.py::RequestsTestCase::test_x PASSED [ 16%]"
PYTEST_RESULT_LINE = re.compile(r"^(\S+::\S+)\s+(PASSED|FAILED|ERROR)\b", re.MULTILINE)
PYTEST_STATUS_MAP = {"PASSED": "ok", "FAILED": "FAIL", "ERROR": "ERROR"}


def _django_labels(meta):
    labels = []
    for t in meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"]:
        name, cls = t.rsplit(" (", 1)
        labels.append(f"{cls.rstrip(')')}.{name}")
    return labels


def _django_parse(output):
    return {f"{cls}.{name}": status for name, cls, status in DJANGO_RESULT_LINE.findall(output)}


def _pytest_labels(meta):
    return meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"]


def _pytest_parse(output):
    return {nodeid: PYTEST_STATUS_MAP[status] for nodeid, status in PYTEST_RESULT_LINE.findall(output)}


# sympy: "test_issue_11617 ok" -- kein Datei-/Klassenbezug im Namen selbst.
SYMPY_RESULT_LINE = re.compile(r"^(test_\S+)\s+(ok|F|E)\b", re.MULTILINE)
SYMPY_STATUS_MAP = {"ok": "ok", "F": "FAIL", "E": "ERROR"}


def _sympy_labels(meta):
    # Bare Namen, wie sie auch in FAIL_TO_PASS/PASS_TO_PASS stehen --
    # welche Datei das ist, wird separat aus test.patch ermittelt.
    return meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"]


def _sympy_parse(output):
    return {name: SYMPY_STATUS_MAP[s] for name, s in SYMPY_RESULT_LINE.findall(output)}


def _test_file_from_patch(task_dir):
    """sympys FAIL_TO_PASS/PASS_TO_PASS nennen keine Datei -- wir nehmen die
    Datei, die test.patch selbst aendert (dort werden die Tests definiert)."""
    text = (task_dir / "test.patch").read_text()
    match = re.search(r"^diff --git a/(\S+) b/\S+", text, re.MULTILINE)
    return match.group(1)


# TRUVENT_APPLY_OK ist ein Marker, kein Fehlertext-Rateversuch: Wir pruefen
# spaeter nur, ob diese Zeile in der Ausgabe steht, statt bekannte
# git-apply-Fehlermeldungen zu erraten (die je nach git-Version/Locale/
# Fehlerart variieren koennen). Fehlt der Marker, ist EGAL welcher Fehler
# beim Patchen aufgetreten ist -- der Patch hat nicht angewendet.
_APPLY_PATCHES = (
    "cd /testbed && git apply /patches/test.patch && git apply /patches/gold.patch "
    "&& echo TRUVENT_APPLY_OK"
)
_ACTIVATE = "source /opt/miniconda3/etc/profile.d/conda.sh && conda activate testbed"

# -p no:randomly / -p no:xdist erzwingen feste Reihenfolge und keine
# Parallelitaet, AUCH wenn das Zielrepo diese Plugins selbst per
# pytest.ini/setup.cfg (addopts) aktiviert haette -- ohne diesen Zwang
# wuerden wir uns nur darauf verlassen, dass kein Repo das tut. Sicher
# auch wenn die Plugins gar nicht installiert sind (pytest ignoriert
# "no:X" fuer nicht registrierte Plugins).
_PYTEST_CMD = "pytest -p no:randomly -p no:xdist -p no:cacheprovider {labels} -v"

REPO_CONFIGS = {
    "django/django": {
        "labels": _django_labels,
        "parse": _django_parse,
        "inner_cmd": (
            f"{_APPLY_PATCHES} && {_ACTIVATE} && "
            "python tests/runtests.py --settings=test_sqlite --parallel 1 -v 2 {labels}"
        ),
    },
    "psf/requests": {
        "labels": _pytest_labels,
        "parse": _pytest_parse,
        "inner_cmd": f"{_APPLY_PATCHES} && {_ACTIVATE} && {_PYTEST_CMD}",
    },
    "pylint-dev/pylint": {
        "labels": _pytest_labels,
        "parse": _pytest_parse,
        "inner_cmd": f"{_APPLY_PATCHES} && {_ACTIVATE} && {_PYTEST_CMD}",
    },
    "pytest-dev/pytest": {
        "labels": _pytest_labels,
        "parse": _pytest_parse,
        "inner_cmd": f"{_APPLY_PATCHES} && {_ACTIVATE} && {_PYTEST_CMD}",
    },
    "sympy/sympy": {
        "labels": _sympy_labels,
        "parse": _sympy_parse,
        # --no-subprocess: bin/test startet sonst einen Subprozess, der
        # Hash-Randomisierung wieder aktivieren kann -- widerspricht unserem
        # PYTHONHASHSEED=0-Pin.
        "inner_cmd": f"{_APPLY_PATCHES} && {_ACTIVATE} && python bin/test --no-subprocess -v {{test_file}}",
    },
}

# Instanzen, deren offizielles SWE-bench-Image eine fehlende Abhaengigkeit
# hatte. Einmalig lokal gefixt (siehe git-Commit-Message) und als eigenes
# Image commited -- entspricht dem Pin "Image einmal bauen, dann nur laufen
# lassen" aus phase0.md.
IMAGE_OVERRIDES = {
    "pylint-dev__pylint-4661": "truvent/sweb.eval.x86_64.pylint-dev_1776_pylint-4661.fixed:latest",
}


def load_meta(instance_id):
    with open(TASKS_DIR / instance_id / "meta.json") as f:
        return json.load(f)


def image_name(instance_id):
    if instance_id in IMAGE_OVERRIDES:
        return IMAGE_OVERRIDES[instance_id]
    suffix = instance_id.replace("__", "_1776_")
    return f"swebench/sweb.eval.x86_64.{suffix}:latest"


def expected_labels(meta):
    return REPO_CONFIGS[meta["repo"]]["labels"](meta)


def parse_results(output, meta):
    return REPO_CONFIGS[meta["repo"]]["parse"](output)


def run_once(instance_id):
    meta = load_meta(instance_id)
    config = REPO_CONFIGS[meta["repo"]]
    task_dir = TASKS_DIR / instance_id
    labels = expected_labels(meta)
    test_file = _test_file_from_patch(task_dir)
    inner_cmd = config["inner_cmd"].format(labels=" ".join(labels), test_file=test_file)

    docker_cmd = [
        "docker", "run", "--rm",
        "--platform", "linux/amd64",
        "--network", "none",
        "-e", "PYTHONHASHSEED=0",
        "-e", "PYTHONIOENCODING=UTF-8",
        "-e", "TZ=UTC",
        "-e", "OMP_NUM_THREADS=1",
        "-e", "OPENBLAS_NUM_THREADS=1",
        "-e", "MKL_NUM_THREADS=1",
        "-v", f"{task_dir.resolve()}:/patches:ro",
        image_name(instance_id),
        "bash", "-c", inner_cmd,
    ]

    result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=300)
    return result.stdout + result.stderr, meta


def check(instance_id):
    output, meta = run_once(instance_id)
    expected = expected_labels(meta)
    actual = parse_results(output, meta)

    missing = [l for l in expected if l not in actual]
    failed = [l for l in expected if actual.get(l) not in (None, "ok")]

    print(f"{instance_id}: {len(actual)} Tests erfasst, {len(expected)} erwartet")
    if missing:
        print(f"  FEHLEND (kein Ergebnis geparst): {missing}")
    if failed:
        print(f"  FEHLGESCHLAGEN: {[(l, actual[l]) for l in failed]}")
    if not missing and not failed:
        print("  ALLE TESTS OK")
    return not missing and not failed


if __name__ == "__main__":
    instance_id = sys.argv[1] if len(sys.argv) > 1 else "django__django-10880"
    ok = check(instance_id)
    sys.exit(0 if ok else 1)

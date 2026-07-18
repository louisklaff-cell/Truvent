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


_APPLY_PATCHES = "cd /testbed && git apply /patches/test.patch && git apply /patches/gold.patch"
_ACTIVATE = "source /opt/miniconda3/etc/profile.d/conda.sh && conda activate testbed"

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
        "inner_cmd": f"{_APPLY_PATCHES} && {_ACTIVATE} && pytest {{labels}} -v",
    },
    "pylint-dev/pylint": {
        "labels": _pytest_labels,
        "parse": _pytest_parse,
        "inner_cmd": f"{_APPLY_PATCHES} && {_ACTIVATE} && pytest {{labels}} -v",
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
    inner_cmd = config["inner_cmd"].format(labels=" ".join(labels))

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

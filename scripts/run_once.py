"""Phase 0, Schritt 2: eine Aufgabe, ein Lauf, Ergebnis parsen."""
import json
import re
import subprocess
import sys
from pathlib import Path

TASKS_DIR = Path(__file__).parent.parent / "tasks"

# Repo-spezifischer Testbefehl. Django nutzt sein eigenes runtests.py,
# kein pytest -- andere Repos (sympy, pytest, pylint, requests) kommen
# in Schritt 4 dazu, jeweils mit eigenem Befehl.
DJANGO_TEST_CMD = (
    "cd /testbed && "
    "git apply /patches/test.patch && "
    "git apply /patches/gold.patch && "
    "source /opt/miniconda3/etc/profile.d/conda.sh && conda activate testbed && "
    "python tests/runtests.py --settings=test_sqlite --parallel 1 -v 2 {labels}"
)

# Zeilen wie: "test_count (aggregation.tests.AggregateTestCase) ... ok"
RESULT_LINE = re.compile(r"^(.+?) \((.+?)\) \.\.\. (ok|FAIL|ERROR)$", re.MULTILINE)


def load_meta(instance_id):
    with open(TASKS_DIR / instance_id / "meta.json") as f:
        return json.load(f)


def to_dotted_labels(test_names):
    labels = []
    for t in test_names:
        name, cls = t.rsplit(" (", 1)
        labels.append(f"{cls.rstrip(')')}.{name}")
    return labels


def image_name(instance_id):
    suffix = instance_id.replace("__", "_1776_")
    return f"swebench/sweb.eval.x86_64.{suffix}:latest"


def run_once(instance_id):
    meta = load_meta(instance_id)
    task_dir = TASKS_DIR / instance_id
    labels = to_dotted_labels(meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"])
    inner_cmd = DJANGO_TEST_CMD.format(labels=" ".join(labels))

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


def parse_results(output):
    return {f"{cls}.{name}": status for name, cls, status in RESULT_LINE.findall(output)}


def check(instance_id):
    output, meta = run_once(instance_id)
    expected_labels = to_dotted_labels(meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"])
    actual = parse_results(output)

    missing = [l for l in expected_labels if l not in actual]
    failed = [l for l in expected_labels if actual.get(l) not in (None, "ok")]

    print(f"{instance_id}: {len(actual)} Tests erfasst, {len(expected_labels)} erwartet")
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

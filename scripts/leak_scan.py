"""Lackmustest 1, Teil 1: Leak-Scan.

Prueft zwei Dinge pro Aufgabe, BEVOR irgendein Patch angewendet wird
(der Container steht also noch auf dem Stand vor dem Fix):

1. Git-Historie: sind ueber Tags/Branches Commits erreichbar, die auf
   dem aktuellen Branch (HEAD rueckwaerts) nicht sichtbar sind? Das
   waere ein Leck -- ein Agent koennte sich die echte Zukunft (und
   damit moeglicherweise den echten Fix) ansehen.
2. Verdaechtige Schluesselwoerter (TODO, FIXME, "issue #", ...) in
   genau den Dateien, die der Gold-Patch aendert -- koennten Hinweise
   auf die Loesung sein, die schon im Code stehen.
"""
import re
import sys
from pathlib import Path

from run_once import image_name, load_meta, run_docker_with_cleanup

TASKS_DIR = Path(__file__).parent.parent / "tasks"

SUSPICIOUS_PATTERN = re.compile(r"\b(TODO|FIXME|XXX|HACK|issue #\d+|bug)\b", re.IGNORECASE)


def _files_from_patch(patch_path):
    text = patch_path.read_text()
    return re.findall(r"^diff --git a/(\S+) b/\S+", text, re.MULTILINE)


def _run_in_container(instance_id, inner_cmd):
    docker_cmd = [
        "docker", "run", "--rm",
        "--platform", "linux/amd64",
        "--network", "none",
        image_name(instance_id),
        "bash", "-c", inner_cmd,
    ]
    return run_docker_with_cleanup(docker_cmd, timeout=120)


def check_git_history_leak(instance_id):
    inner_cmd = (
        "cd /testbed && "
        "git log --oneline | sort > /tmp/branch.txt && "
        "git log --all --oneline | sort > /tmp/all.txt && "
        "diff /tmp/branch.txt /tmp/all.txt"
    )
    output = _run_in_container(instance_id, inner_cmd)
    extra_lines = [l for l in output.splitlines() if l.startswith(">")]
    return extra_lines


def check_suspicious_comments(instance_id, files):
    findings = {}
    for f in files:
        inner_cmd = f"cd /testbed && cat {f} 2>/dev/null || true"
        content = _run_in_container(instance_id, inner_cmd)
        matches = SUSPICIOUS_PATTERN.findall(content)
        if matches:
            findings[f] = matches
    return findings


def scan(instance_id):
    meta = load_meta(instance_id)
    files = _files_from_patch(TASKS_DIR / instance_id / "gold.patch")

    print(f"{instance_id} ({meta['repo']}, Dateien: {', '.join(files)})")

    extra_commits = check_git_history_leak(instance_id)
    if extra_commits:
        print(f"  GIT-LECK: {len(extra_commits)} Commits nur ueber --all erreichbar")
        for line in extra_commits[:3]:
            print(f"    {line}")
    else:
        print("  Git-Historie: kein Leck")

    comment_findings = check_suspicious_comments(instance_id, files)
    if comment_findings:
        for f, matches in comment_findings.items():
            print(f"  VERDAECHTIGE KOMMENTARE in {f}: {matches}")
    else:
        print("  Kommentare: keine verdaechtigen Schluesselwoerter")

    return not extra_commits and not comment_findings


if __name__ == "__main__":
    instance_id = sys.argv[1] if len(sys.argv) > 1 else "django__django-10880"
    ok = scan(instance_id)
    sys.exit(0 if ok else 1)

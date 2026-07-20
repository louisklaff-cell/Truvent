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

Beide Pruefungen laufen in EINEM Container-Aufruf statt in einem pro
Datei -- spart Container-Startaufwand, ohne dass sich am Ergebnis
etwas aendert (reine Konsolidierung, keine inhaltliche Aenderung).
"""
import re
import sys
from pathlib import Path

from run_once import image_name, load_meta, run_docker_with_cleanup

TASKS_DIR = Path(__file__).parent.parent / "tasks"

SUSPICIOUS_PATTERN = re.compile(r"\b(TODO|FIXME|XXX|HACK|issue #\d+|bug)\b", re.IGNORECASE)

_GIT_MARKER = "===TRUVENT_GIT_DIFF==="
_FILE_MARKER = "===TRUVENT_FILE:{f}==="
_FILE_END_MARKER = "===TRUVENT_FILE_END==="


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


def _build_combined_cmd(files):
    git_part = (
        "cd /testbed && "
        "git log --oneline | sort > /tmp/branch.txt && "
        "git log --all --oneline | sort > /tmp/all.txt && "
        f"echo '{_GIT_MARKER}' && diff /tmp/branch.txt /tmp/all.txt"
    )
    file_parts = [
        f"echo '{_FILE_MARKER.format(f=f)}' && cat {f} 2>/dev/null; echo '{_FILE_END_MARKER}'"
        for f in files
    ]
    return " ; ".join([git_part] + file_parts)


def scan(instance_id):
    meta = load_meta(instance_id)
    files = _files_from_patch(TASKS_DIR / instance_id / "gold.patch")

    print(f"{instance_id} ({meta['repo']}, Dateien: {', '.join(files)})")

    output = _run_in_container(instance_id, _build_combined_cmd(files))

    # Git-Teil: alles zwischen dem Git-Marker und dem ersten Datei-Marker
    # (oder Ende, falls keine Dateien).
    git_section = output.split(_GIT_MARKER, 1)[1] if _GIT_MARKER in output else ""
    if files:
        first_file_marker = _FILE_MARKER.format(f=files[0])
        git_section = git_section.split(first_file_marker, 1)[0]
    extra_commits = [l for l in git_section.splitlines() if l.startswith(">")]

    if extra_commits:
        print(f"  GIT-LECK: {len(extra_commits)} Commits nur ueber --all erreichbar")
        for line in extra_commits[:3]:
            print(f"    {line}")
    else:
        print("  Git-Historie: kein Leck")

    comment_findings = {}
    for f in files:
        marker = _FILE_MARKER.format(f=f)
        if marker not in output:
            continue
        content = output.split(marker, 1)[1].split(_FILE_END_MARKER, 1)[0]
        matches = SUSPICIOUS_PATTERN.findall(content)
        if matches:
            comment_findings[f] = matches

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

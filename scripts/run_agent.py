"""Mini-Phase-0.5: ein echter Coding-Agent (Claude via API) versucht,
dieselben 5 Aufgaben aus Phase 0 zu loesen. Kein voller autonomer
Agent mit Werkzeugzugriff -- Problem + Dateiinhalt rein, Patch raus.
Testfrage: verarbeitet unser Harness echten KI-Output ueberhaupt
korrekt (nicht nur unsere eigenen sauberen Gold Patches/Mutanten)?
"""
import os
import re
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from mutation_test import check_mutant
from run_once import load_meta

load_dotenv()

TASKS_DIR = Path(__file__).parent.parent / "tasks"

SYSTEM_PROMPT = (
    "You are an expert software engineer fixing a real bug. You will be given "
    "a problem description and the current content of the relevant file(s), "
    "with line numbers for reference. Produce a fix as a unified diff patch "
    "in git format (diff --git, ---/+++ headers, @@ hunk headers with correct "
    "line numbers) that could be applied with `git apply`. "
    "Output ONLY the diff, wrapped in a single ```diff code block. No other text."
)


def _files_from_gold_patch(instance_id):
    text = (TASKS_DIR / instance_id / "gold.patch").read_text()
    return re.findall(r"^diff --git a/(\S+) b/\S+", text, re.MULTILINE)


def _file_content_from_container(instance_id, filepath):
    from run_once import image_name
    import subprocess

    result = subprocess.run(
        ["docker", "run", "--rm", "--platform", "linux/amd64",
         image_name(instance_id), "bash", "-c", f"cat -n /testbed/{filepath}"],
        capture_output=True, text=True, timeout=60,
    )
    return result.stdout


def _extract_patch(response_text):
    match = re.search(r"```diff\n(.*?)```", response_text, re.DOTALL)
    if not match:
        match = re.search(r"```\n(.*?)```", response_text, re.DOTALL)
    return match.group(1) if match else response_text


def generate_patch(instance_id, model):
    problem = (TASKS_DIR / instance_id / "problem_statement.txt").read_text()
    files = _files_from_gold_patch(instance_id)

    file_sections = []
    for f in files:
        content = _file_content_from_container(instance_id, f)
        file_sections.append(f"## Current file: {f}\n```\n{content}\n```")

    user_message = f"## Problem\n{problem}\n\n" + "\n\n".join(file_sections)

    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    text_blocks = [block.text for block in response.content if block.type == "text"]
    return _extract_patch("\n".join(text_blocks))


# check_mutant() ist fuer absichtlich FALSCHE Patches benannt (FALSE_ACCEPT
# = schlecht). Bei einem echten Agentenversuch ist "alle Tests bestanden"
# aber das gewuenschte Ergebnis -- deshalb hier umbenannt.
VERDICT_LABELS = {
    "MUTANT_UNGUELTIG": "PATCH_UNGUELTIG",   # Patch liess sich nicht anwenden
    "KORREKT_ABGELEHNT": "AGENT_GESCHEITERT", # mind. ein Test schlaegt fehl
    "FALSE_ACCEPT": "AGENT_ERFOLGREICH",      # alle Tests bestanden
}


def run_agent_attempt(instance_id, model, run_number, out_dir):
    patch_text = generate_patch(instance_id, model)
    patch_path = out_dir / f"{model}_run{run_number}.patch"
    patch_path.write_text(patch_text)

    raw_verdict, detail = check_mutant(instance_id, patch_path)
    return VERDICT_LABELS[raw_verdict], detail, patch_path


if __name__ == "__main__":
    instance_id = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "claude-sonnet-5"
    run_number = sys.argv[3] if len(sys.argv) > 3 else "1"

    out_dir = TASKS_DIR / instance_id / "agent_patches"
    out_dir.mkdir(exist_ok=True)

    verdict, detail, patch_path = run_agent_attempt(instance_id, model, run_number, out_dir)
    print(f"{instance_id} / {model} / Lauf {run_number}: {verdict}")
    print(f"  Patch gespeichert: {patch_path}")
    if detail:
        print(f"  {detail}")

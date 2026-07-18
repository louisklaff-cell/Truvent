import json

import requests

WHITELIST_REPOS = {
    "django/django",
    "sympy/sympy",
    "sphinx-doc/sphinx",
    "pytest-dev/pytest",
    "pylint-dev/pylint",
    "psf/requests",
    "pallets/flask",
}

RANDOM_TIME_SIGNALS = ["random.", "datetime.now(", "time.sleep(", "time.time("]

url = "https://datasets-server.huggingface.co/rows"
base_params = {
    "dataset": "princeton-nlp/SWE-bench_Verified",
    "config": "default",
    "split": "test",
}

candidates = []
offset = 0
page_size = 100

while True:
    params = {**base_params, "offset": offset, "length": page_size}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    rows = response.json()["rows"]

    if not rows:
        break

    for entry in rows:
        row = entry["row"]
        if row["repo"] not in WHITELIST_REPOS:
            continue

        fail_to_pass = json.loads(row["FAIL_TO_PASS"])
        combined_text = row["patch"] + row["test_patch"]
        signals = [s for s in RANDOM_TIME_SIGNALS if s in combined_text]

        candidates.append(
            {
                "instance_id": row["instance_id"],
                "repo": row["repo"],
                "fail_to_pass_count": len(fail_to_pass),
                "signals": signals,
            }
        )

    offset += page_size

candidates.sort(key=lambda c: (len(c["signals"]), c["fail_to_pass_count"]))

print(f"{'instance_id':45s} {'repo':20s} {'F2P':>4s}  signals")
for repo in sorted(WHITELIST_REPOS):
    repo_candidates = [c for c in candidates if c["repo"] == repo]
    for c in repo_candidates[:2]:
        signal_str = ",".join(c["signals"]) if c["signals"] else "-"
        print(f"{c['instance_id']:45s} {c['repo']:20s} {c['fail_to_pass_count']:4d}  {signal_str}")
    if not repo_candidates:
        print(f"(keine Kandidaten fuer {repo})")

print(f"\n{len(candidates)} Kandidaten insgesamt in der Whitelist (von 500).")

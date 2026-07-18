from collections import Counter

import requests

url = "https://datasets-server.huggingface.co/rows"
base_params = {
    "dataset": "princeton-nlp/SWE-bench_Verified",
    "config": "default",
    "split": "test",
}

repo_counts = Counter()
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
        repo_counts[entry["row"]["repo"]] += 1

    offset += page_size

for repo, count in repo_counts.most_common():
    print(f"{count:4d}  {repo}")

print(f"\nGesamt: {sum(repo_counts.values())} Instanzen")

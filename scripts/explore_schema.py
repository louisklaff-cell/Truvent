import requests

url = "https://datasets-server.huggingface.co/rows"
params = {
    "dataset": "princeton-nlp/SWE-bench_Verified",
    "config": "default",
    "split": "test",
    "offset": 0,
    "length": 1,
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

row = response.json()["rows"][0]["row"]
for key, value in row.items():
    preview = str(value)[:120]
    print(f"{key}: {preview}")

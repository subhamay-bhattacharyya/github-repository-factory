import json
from pprint import pprint

GITHUB_REPO_FILE = "github-repo.json"

all_gists = []
with open(GITHUB_REPO_FILE, "r") as f:
    data = json.load(f)


for key,val in data.items():
    for iac in val.get('iac', []):
        filename = f"{key}-{val.get('category')}-{iac}.json"
        data = {
        "id": None,
        "filename": filename,
        "description": f"Gist for {filename}",
        "content": {
            "schemaVersion": 1,
            "label": "status",
            "message": "not started",
            "color": "red",
            "style": "flat"
            },
        "operation": "create"
        }
        all_gists.append(data)

with open("gists.json", "w") as f:
    json.dump(all_gists, f, indent=2, ensure_ascii=False)
    print("📂 Gists written to gists.json")

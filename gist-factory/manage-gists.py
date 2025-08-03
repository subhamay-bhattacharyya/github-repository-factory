import requests
import json
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

INPUT_FILE = "gists.json"
OUTPUT_MAPPING = {}
UPDATED_ENTRIES = []

with open(INPUT_FILE, "r") as f:
    gist_entries = json.load(f)

for entry in gist_entries:

    operation = entry.get("operation", "").lower()
    gist_id = entry.get("id", None)
    if operation == "fetched":
        UPDATED_ENTRIES.append(entry)
    elif operation == "create":
        print(f"Creating Gist: {entry}")
        payload = {
            "description": f"Gist for {entry.get('filename')}",
            "public": False,
            "files": {
                entry.get("filename"): {
                    "content": json.dumps(entry.get("content", {}), indent=2)
                }
            }
        }
        response = requests.post("https://api.github.com/gists", headers=HEADERS, json=payload)
        if response.status_code == 201:
            gist_data = response.json()
            file_info = list(gist_data["files"].values())[0]
            entry.update({"id": gist_data["id"], "description": gist_data["description"], "raw_url": file_info["raw_url"], "operation": "fetched"})
            UPDATED_ENTRIES.append(entry)
            print(f"✅ Created Gist: {gist_data['html_url']}")
    elif operation == "delete" and gist_id:
        response = requests.delete(f"https://api.github.com/gists/{gist_id}", headers=HEADERS)
        if response.status_code == 204:
            print(f"🗑️ Deleted Gist with ID: {gist_id}")
        else:
            print(f"❌ Failed to delete Gist for {name}: {response.status_code}")
            print(response.json())
    elif operation == "update" and gist_id:
        payload = {
            "files": {
                entry.get("filename"): {
                    "content": json.dumps(entry.get("content", {}), indent=2)
                }
            }
        }
        response = requests.patch(f"https://api.github.com/gists/{gist_id}", headers=HEADERS, json=payload)
        if response.status_code == 200:
            gist_data = response.json()
            file_info = list(gist_data["files"].values())[0]
            entry.update({"id": gist_data["id"], "description": gist_data["description"], "raw_url": file_info["raw_url"], "operation": "fetched"})
            UPDATED_ENTRIES.append(entry)
            print(f"🔄 Updated Gist: {gist_data['html_url']}")

with open("all-gists.json", "w") as f:
    json.dump(UPDATED_ENTRIES, f, indent=2, ensure_ascii=False)

print("\n📂 Gists written to all-gists.json")
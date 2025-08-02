import requests
import json
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

INPUT_FILE = "gists_input.json"
OUTPUT_MAPPING = {}
UPDATED_ENTRIES = []

with open(INPUT_FILE, "r") as f:
    gist_entries = json.load(f)

for entry in gist_entries:
    name = entry.get("gist-name")
    operation = entry.get("operation", "").lower()
    status = entry.get("status", "draft")
    gist_id = entry.get("id")
    filename = f"{name}.json"

    json_content = {
        "title": name.replace("-", " ").title(),
        "created_by": "Terraform Python Gist Manager",
        "status": status
    }

    if operation == "create":
        payload = {
            "description": f"Gist for {name}",
            "public": False,
            "files": {
                filename: {
                    "content": json.dumps(json_content, indent=2)
                }
            }
        }
        response = requests.post("https://api.github.com/gists", headers=HEADERS, json=payload)
        if response.status_code == 201:
            gist_data = response.json()
            file_info = list(gist_data["files"].values())[0]
            entry["id"] = gist_data["id"]
            UPDATED_ENTRIES.append(entry)
            OUTPUT_MAPPING[filename] = {
                "id": gist_data["id"],
                "raw_url": file_info["raw_url"]
            }
            print(f"✅ Created Gist: {gist_data['html_url']}")
        else:
            print(f"❌ Failed to create Gist for {name}: {response.status_code}")
            print(response.json())
            UPDATED_ENTRIES.append(entry)

    elif operation == "update" and gist_id:
        payload = {
            "files": {
                filename: {
                    "content": json.dumps(json_content, indent=2)
                }
            }
        }
        response = requests.patch(f"https://api.github.com/gists/{gist_id}", headers=HEADERS, json=payload)
        if response.status_code == 200:
            gist_data = response.json()
            file_info = list(gist_data["files"].values())[0]
            OUTPUT_MAPPING[filename] = {
                "id": gist_data["id"],
                "raw_url": file_info["raw_url"]
            }
            UPDATED_ENTRIES.append(entry)
            print(f"🔄 Updated Gist: {gist_data['html_url']}")
        else:
            print(f"❌ Failed to update Gist for {name}: {response.status_code}")
            print(response.json())
            UPDATED_ENTRIES.append(entry)

    elif operation == "delete" and gist_id:
        response = requests.delete(f"https://api.github.com/gists/{gist_id}", headers=HEADERS)
        if response.status_code == 204:
            print(f"🗑️ Deleted Gist with ID: {gist_id}")
        else:
            print(f"❌ Failed to delete Gist for {name}: {response.status_code}")
            print(response.json())
    else:
        print(f"⚠️ Skipping invalid entry: {entry}")
        UPDATED_ENTRIES.append(entry)

# Save mapping (optional)
with open("gists_output.json", "w") as f:
    json.dump(OUTPUT_MAPPING, f, indent=4)

# Overwrite input file with updated entries (excluding deletes)
with open(INPUT_FILE, "w") as f:
    json.dump(UPDATED_ENTRIES, f, indent=4)

print(f"📄 Updated {INPUT_FILE} with current state.")

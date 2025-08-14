import requests
import os
import sys
import json
from pprint import pprint

# Get GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ Error: Environment variable 'GITHUB_TOKEN' is not set.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_secret_gists():
    page = 1
    per_page = 100
    secret_gists = []

    while True:
        url = f"https://api.github.com/gists?per_page={per_page}&page={page}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ Failed to fetch gists: {response.status_code}")
            print(response.json())
            break

        gists = response.json()
        if not gists:
            break

        for gist in gists:
            if not gist.get("public", True):
                gist_id = gist["id"]
                description = gist.get("description", "")
                files = gist.get("files", {})

                for filename, file_info in files.items():
                    raw_url = file_info.get("raw_url")
                    content = None
                    if raw_url:
                        content_response = requests.get(raw_url, headers=HEADERS)
                        if content_response.status_code == 200:
                            content = content_response.text
                        else:
                            # content = f"[Failed to fetch content: {content_response.status_code}]"
                            try:
                                content = json.loads(content)  # Ensure content is JSON serializable
                                content = {
                                    "schemaVersion": content.get("schemaVersion", None),
                                    "label": content.get("label",None),
                                    "message": content.get("message",None),
                                    "color": content.get("color",None),
                                    "style": content.get("style",None)
                                }
                            except json.JSONDecodeError:
                                content = f"[Content not JSON serializable]"
                                content = {}

                    secret_gists.append({
                        "id": gist_id,
                        "filename": filename,
                        "description": description,
                        "content": content,
                        "operation": "fetched",
                        "raw_url": raw_url
                    })

        page += 1

    return secret_gists

if __name__ == "__main__":
    gists = fetch_secret_gists()
    gist_ids = {}
    if gists:
        print(f"🔐 Found {len(gists)} secret gist file(s):")
        # Convert stringified JSON in 'content' to dicts where possible
        for gist in gists:
            content = gist.get("content")
            if isinstance(content, str):
                try:
                    gist["content"] = json.loads(content)
                except Exception:
                    pass  # Leave as string if not valid JSON

        for gist in gists:
            gist_name = gist.get("filename", "").split(".")[0]
            if len(gist_name.split("-")) == 3 and gist_name.split("-")[0] in ["0001","0002"] and gist_name.split("-")[1] == "storage":
                gist_ids[gist_name] = {
                    "id": gist.get("id"),
                    "raw_url": gist.get("raw_url", "")
                }

        with open("all-gists.json", "w") as f:
            json.dump(gists, f, indent=2, ensure_ascii=False)
        print("\n📂 Gists written to all-gists.json")

        with open("gist-ids.json", "w") as f:
            json.dump(gist_ids, f, indent=2, ensure_ascii=False)
        print("📂 Gist IDs written to gist-ids.json")
    else:
        print("ℹ️ No secret gists found.")
#!/usr/bin/env bash
set -euo pipefail

OUT="all-gists-extracted.json"
echo "[" > "$OUT"
first=1

# Requires: gh auth login
for id in $(gh api --paginate /gists | jq -r '.[].id'); do
  g=$(gh api "/gists/$id")

  public=$(jq -r '.public' <<<"$g")
  gist_type=$([ "$public" = "true" ] && echo "public" || echo "secret")

  # pick the first file in the gist
  fname=$(jq -r '.files | keys[0]' <<<"$g")
  fobj=$(jq -r --arg f "$fname" '.files[$f]' <<<"$g")
  truncated=$(jq -r '.truncated // false' <<<"$fobj")

  if [ "$truncated" = "true" ]; then
    raw=$(jq -r '.raw_url' <<<"$fobj")
    content=$(curl -sL "$raw")
  else
    content=$(jq -r '.content // ""' <<<"$fobj")
  fi

  # escape content safely for JSON
  content_json=$(printf '%s' "$content" | jq -Rs .)

  obj=$(jq -n \
    --arg id "$id" \
    --arg filename "$fname" \
    --arg description "Gist for $fname" \
    --arg gist_type "$gist_type" \
    --argjson content "$content_json" \
    '{
      id: $id,
      filename: $filename,
      description: $description,
      content: ($content | fromjson),
      "gist-type": $gist_type,
      operation: "skip"
    }')

  if [ $first -eq 0 ]; then echo "," >> "$OUT"; fi
  first=0
  echo "$obj" >> "$OUT"
done

echo "]" >> "$OUT"
echo "Wrote $OUT"

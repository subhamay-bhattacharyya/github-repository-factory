"""
Maintain GitHub Gists
This script manages GitHub gists based on a JSON file input.
It supports creating, updating, and deleting gists, as well as skipping existing ones.
It can also perform a dry run to show what would be done without making any changes.
"""

import argparse
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import Counter
import requests


API_URL = "https://api.github.com/gists"


def get_status(item):
    """
    Determines the status of an item based on its operation type or presence of an ID.
    Args:
        item (dict): A dictionary representing an item, which may contain the keys
        'operation' and/or 'id'.
    Returns:
        str: The status of the item, which can be one of the following:
            - "Deleted" if the operation is 'delete'
            - "Updated" if the operation is 'update'
            - "Created" if the operation is 'create'
            - "Skipped" if the item has an 'id' key with a truthy value or if none of
            the above conditions are met
    """

    if "operation" in item:
        if item["operation"] == "delete":
            return "Deleted"
        elif item["operation"] == "update":
            return "Updated"
        elif item["operation"] == "create":
            return "Created"
    if "id" in item and item.get("id"):
        return "Skipped"
    return "Skipped"


def get_headers(token: str) -> Dict[str, str]:
    """
    Generate HTTP headers for GitHub API requests.

    Args:
        token (str): GitHub personal access token. If provided, the Authorization header
        is included.

    Returns:
        Dict[str, str]: Dictionary of HTTP headers for GitHub API requests.

    Returns the headers required for GitHub API requests.
    If a token is provided, it includes the Authorization header.
    """
    headers = {
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def load_json(path: Path) -> List[Dict[str, Any]]:
    """
    Load a JSON file from the given path and return its contents as a list of dictionaries.
    Raises an error and exits if the file cannot be read or does not contain a list.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Input JSON must be a list of gist items.")
        return data
    except (OSError, json.JSONDecodeError) as e:
        print(f"❌ Failed to read JSON from {path}: {e}", file=sys.stderr)
        sys.exit(1)


def parse_args():
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Maintain GitHub Gists from a JSON file."
    )
    parser.add_argument("--input", required=True, help="Path to the input JSON file.")
    parser.add_argument(
        "--output", help="Path to the output JSON file (defaults to input file)."
    )
    parser.add_argument("--token", help="GitHub token or path to token file.")
    return parser.parse_args()


def segregate_gists(
    items: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str], List[Dict[str, Any]]]:
    """
    Segregate items into:
        - to_create: items without 'gist_id' and operation is 'create' or missing
        - to_update: items with 'gist_id' and operation is 'update'
        - to_delete: gist_ids from items with 'gist_id' and operation is 'delete'
        - to_skip: items that do not match any of the above
    """
    to_create = []
    to_update = []
    to_delete = []
    to_skip = []
    for item in items:
        gist_id = item.get("id")
        operation = item.get("operation", None)
        if operation == "delete" and gist_id:
            to_delete.append(gist_id)
        elif operation == "update" and gist_id:
            to_update.append(item)
        elif (operation == "create" or operation is None) and not gist_id:
            to_create.append(item)
        else:
            to_skip.append(item)  # No operation, or unrecognized operation
    return to_create, to_update, to_delete, to_skip


def create_gists(
    session: requests.Session,
    items: List[Dict[str, Any]],
    token: str,
    dry_run: bool = False,
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """
    Create GitHub gists for the given items (dicts without 'gist_id').
    Updates each item in-place with the new 'gist_id' if creation succeeds.
    Returns the list of items with updated gist_ids.
    """

    created_items = []
    if debug:
        print("First two gists to create:")
        for item in items[:2]:
            print(json.dumps(item, indent=2))

    for idx, item in enumerate(items, start=1):
        if "id" in item and item.get("id"):
            if debug:
                print(f"[{idx}] Skipping item with existing id: {item['id']}")
            continue

        payload = {
            "description": f'Gist for {item.get("filename", "untitled.json")}',
            "public": False,
            "files": {
                item.get("filename", "untitled.json"): {
                    "content": json.dumps(item.get("content", {}), indent=2)
                }
            },
        }
        if not payload["files"]:
            print(
                f"❌ [{idx}] No files specified for gist creation; skipping.",
                file=sys.stderr,
            )
            continue
        if dry_run:
            print(f"[DRY RUN] Would create gist: {json.dumps(payload, indent=2)}")
            print("===============================================================")
            continue
        try:
            headers = get_headers(token)
            resp = session.post(API_URL, headers=headers, json=payload, timeout=10)
            if resp.status_code == 201:
                gist_id = resp.json().get("id")
                item.update({"id": gist_id})
                created_items.append(item)
                if debug:
                    gist_url = resp.json().get("html_url")
                    print(f"✅ [{idx}] Created gist: {gist_url}")
            else:
                print(
                    f"❌ [{idx}] Failed to create gist: {resp.status_code} {resp.text}",
                    file=sys.stderr,
                )
        except requests.RequestException as e:
            print(
                f"❌ [{idx}] Network error during gist creation: {e}", file=sys.stderr
            )
    return created_items


def update_gists(
    session: requests.Session,
    items: List[Dict[str, Any]],
    token: str,
    dry_run: bool = False,
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """
    Update existing GitHub gists for the given items (dicts with 'gist_id').
    Returns the list of items that were successfully updated.
    """

    updated_items = []
    if debug:
        print("First two gists to update:")
        for item in items[:2]:
            print(json.dumps(item, indent=2))

    for idx, item in enumerate(items, start=1):
        gist_id = item.get("id")
        if not gist_id:
            if debug:
                print(f"[{idx}] Skipping item without id.")
            continue

        payload = {
            "description": f'Updated gist for {item.get("filename", "untitled.json")}',
            "files": {
                item.get("filename", "untitled.json"): {
                    "content": json.dumps(item.get("content", {}), indent=2)
                }
            },
        }
        print(payload)
        if not payload["files"]:
            print(
                f"❌ [{idx}] No files specified for gist update; skipping.",
                file=sys.stderr,
            )
            continue
        if dry_run:
            print(
                f"[DRY RUN] Would update gist {gist_id}: {json.dumps(payload, indent=2)}"
            )
            print("===============================================================")
            continue
        try:
            headers = get_headers(token)
            resp = session.patch(
                f"{API_URL}/{gist_id}", headers=headers, json=payload, timeout=10
            )
            if resp.status_code == 200:
                updated_items.append(item)
                if debug:
                    gist_url = resp.json().get("html_url")
                    print(f"✅ [{idx}] Updated gist: {gist_url}")
            else:
                print(
                    f"❌ [{idx}] Failed to update gist {gist_id}: {resp.status_code} {resp.text}",
                    file=sys.stderr,
                )
        except requests.RequestException as e:
            print(f"❌ [{idx}] Network error during gist update: {e}", file=sys.stderr)
    return updated_items


def delete_gists(
    session: requests.Session,
    gist_ids: List[str],
    token: str,
    dry_run: bool = False,
    debug: bool = False,
) -> List[str]:
    """
    Delete GitHub gists for the given gist IDs.
    Returns the list of gist IDs that were successfully deleted.
    """

    deleted_ids = []
    if debug:
        print("First two gist IDs to delete:")
        for gist_id in gist_ids[:2]:
            print(gist_id)

    for idx, gist_id in enumerate(gist_ids, start=1):
        if dry_run:
            print(f"[DRY RUN] Would delete gist {gist_id}")
            print("===============================================================")
            continue
        try:
            headers = get_headers(token)
            resp = session.delete(f"{API_URL}/{gist_id}", headers=headers, timeout=10)
            if resp.status_code == 204:
                deleted_ids.append(gist_id)
                if debug:
                    print(f"✅ [{idx}] Deleted gist: {gist_id}")
            else:
                print(
                    f"❌ [{idx}] Failed to delete gist {gist_id}: {resp.status_code} {resp.text}",
                    file=sys.stderr,
                )
        except requests.RequestException as e:
            print(
                f"❌ [{idx}] Network error during gist deletion: {e}", file=sys.stderr
            )
    return deleted_ids


def generate_gist_id_json(all_gists_path, output_path, github_username):
    """
    Generate a JSON file mapping filenames to gist id and raw_url.
    Args:
        all_gists_path (Path): Path to the all-gists.json file.
        output_path (Path): Path to write the gist-id.json file.
        github_username (str): GitHub username for constructing raw_url.
    """
    try:
        with all_gists_path.open("r", encoding="utf-8") as f:
            gists = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Failed to read {all_gists_path}: {e}", file=sys.stderr)
        return

    gist_map = {}
    for item in gists:
        filename = item.get("filename")
        gist_id = item.get("id")
        history = item.get("history", [])
        # Use the latest version SHA if available, else fallback to gist_id
        version = history[0]["version"] if history else ""
        if not (filename and gist_id):
            continue
        raw_url = (
            f"https://gist.githubusercontent.com/{github_username}/{gist_id}/raw/"
            f"{version}/{filename}"
            if version
            else f"https://gist.githubusercontent.com/{github_username}/{gist_id}/raw/{filename}"
        )
        gist_map[filename] = {"id": gist_id, "raw_url": raw_url}

    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(gist_map, f, indent=2)
        print(f"Gist ID JSON written to {output_path}")
    except (OSError, IOError) as e:
        print(f"Failed to write {output_path}: {e}", file=sys.stderr)


def main():
    """
    Main entry point for the script.
    Parses command-line arguments to manage GitHub gists based on a JSON file.
    Supports creating, updating, and deleting gists, as well as skipping existing ones.
    Handles dry-run and debug modes for validation and verbose output.
    Arguments:
        -i, --input         Path to input JSON file (required).
        -o, --output        Path to output JSON file (optional, defaults to input file).
        --token             GitHub token (optional, defaults to GITHUB_TOKEN env var).
        --skip-existing     Skip items that already contain a 'gist_id'.
        --dry-run           Show actions without making API calls.
        --debug             Enable debug output.
    Workflow:
        1. Loads and validates the input JSON file.
        2. Segregates items into create, update, delete, and skip categories.
        3. Performs the requested operations (create/update/delete) on GitHub gists.
        4. Optionally writes the updated data back to the output file.
    """

    parser = argparse.ArgumentParser(
        description="Create GitHub gists from a JSON file and write gist IDs back into it."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to input JSON file (list of gist items).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to write updated JSON. Defaults to in-place update of input file.",
    )
    parser.add_argument(
        "--token",
        help="GitHub token. If omitted, reads from GITHUB_TOKEN env var.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip items that already contain a 'gist_id'.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and show what would be created without calling the API.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output.",
    )

    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or args.input

    if getattr(args, "debug", False):
        print("---------------------------------------------------------")
        print(f"Input file     => {input_path}")
        print(f"Output file    => {output_path}")
        print(f"Skip existing  => {args.skip_existing}")
        print(f"Dry run        => {args.dry_run}")
        print("---------------------------------------------------------")

    if not os.path.isfile(input_path):
        print(f"Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        input_path = Path(args.input).expanduser().resolve()
        output_path = (
            Path(args.output).expanduser().resolve() if args.output else input_path
        )
        items = load_json(input_path)

    except (OSError, json.JSONDecodeError) as e:
        print(f"Failed to load input JSON: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if not isinstance(items, list):
            raise ValueError("Input JSON must be an array of items.")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    session = requests.Session()

    # Example usage:
    to_create, to_update, to_delete, to_skip = segregate_gists(items)
    if getattr(args, "debug", False):
        print(f"To create: {len(to_create)}")
        print(f"To update: {len(to_update)}")
        print(f"To delete: {len(to_delete)}")
        print(f"To skip: {len(to_skip)}")

    print(">>>>>>>>---------------------------------------------------------")
    print(f"Skipped {len(to_skip)} gists.")
    print(">>>>>>>>---------------------------------------------------------")
    if to_create:
        created_items = create_gists(
            session,
            to_create,
            args.token or os.getenv("GITHUB_TOKEN"),
            dry_run=args.dry_run,
            debug=args.debug,
        )
        print(">>>>>>>>---------------------------------------------------------")
        print(f"Created {len(created_items)} gists.")
        print(">>>>>>>>---------------------------------------------------------")
        if getattr(args, "debug", False):
            print("Created gists:")
            for item in created_items:
                print(json.dumps(item, indent=2))

    if to_update:
        updated_items = update_gists(
            session,
            to_update,
            args.token or os.getenv("GITHUB_TOKEN"),
            dry_run=args.dry_run,
            debug=args.debug,
        )
        print(">>>>>>>>---------------------------------------------------------")
        print(f"Updated {len(updated_items)} gists.")
        print(">>>>>>>>---------------------------------------------------------")
        if getattr(args, "debug", False):
            print("Updated gists:")
            for item in updated_items:
                print(json.dumps(item, indent=2))

    if to_delete:
        deleted_items = delete_gists(
            session,
            to_delete,
            args.token or os.getenv("GITHUB_TOKEN"),
            dry_run=args.dry_run,
            debug=args.debug,
        )
        print(">>>>>>>>---------------------------------------------------------")
        print(f"Deleted {len(deleted_items)} gists.")
        print(">>>>>>>>---------------------------------------------------------")
        if getattr(args, "debug", False):
            print("Deleted gists:")
            for item in deleted_items:
                print(json.dumps(item, indent=2))

    # Merge created_items, updated_items, and to_skip if their lengths are more than 0
    merged_items = []
    if to_create and len(created_items) > 0:
        merged_items.extend(created_items)
    if to_update and len(updated_items) > 0:
        merged_items.extend(updated_items)
    if len(to_skip) > 0:
        merged_items.extend(to_skip)
    if len(to_delete) > 0 and len(deleted_items) == 0:
        merged_items.extend(to_delete)


    # Optionally, print or process merged_items as needed
    print("=" * 60)
    if getattr(args, "debug", False):
        print("Merged items:")
        for item in merged_items:
            print(json.dumps(item, indent=2))

    print(f"Merged items - {merged_items}")
    # Write the updated items back to the output file
    if not merged_items:
        print("No items to write back to output file.", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"Writing the file {output_path} ")
        try:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(merged_items, f, indent=2)
            print(f"Updated items written to {output_path}")
        except OSError as e:
            print(f"Failed to write output JSON: {e}", file=sys.stderr)
            sys.exit(1)

    # If merged_items is not empty, print a tabular report
    if merged_items:

        # Prepare table rows
        table = []
        for item in merged_items:
            table.append(
                [
                    item.get("id", "-"),
                    item.get("filename", "-"),
                    get_status(item),
                    item.get("description", "-"),
                ]
            )

        # Print table header
        print("\n## Gist Operation Report\n")
        print("| {:<32} | {:<20} | {:<10} | {:<40} |".format("Gist ID", "Filename", "Status", "Description"))
        print("|" + "-"*34 + "|" + "-"*22 + "|" + "-"*12 + "|" + "-"*40 + "|")
        # Print markdown table header
        print(f"| {'Gist ID':<32} | {'Filename':<20} | {'Status':<10} | {'Description'} |")
        print(f"|{'-'*34}|{'-'*22}|{'-'*12}|{'-'*40}|")
        # Print markdown table rows
        for row in table:
            print(f"| {row[0]:<32} | {row[1]:<20} | {row[2]:<10} | {row[3]:<40} |")
        print("-" * 60)
        for row in table:
            print(f"{row[0]:<32} {row[1]:<20} {row[2]:<10} {row[3]}")
        print("-" * 60)

        # Print summary
        status_counts = Counter(get_status(item) for item in merged_items)
        print("Summary:")
        for status in ["Created", "Updated", "Deleted", "Skipped"]:
            print(f"  {status}: {status_counts.get(status, 0)}")
        print("=" * 60)

        # generate gist_id.json:
        generate_gist_id_json(
            Path("gist-factory/all-gists.json"),
            Path("gist-factory/gist-id.json"),
            "bsubhamay",
        )


if __name__ == "__main__":
    main()

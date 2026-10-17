#!/usr/bin/env python3
"""Audit the nine stephdl/ns8-apps listing criteria (not runtime quality).

By default inspect the published catalog and public GitHub data. --apps overlays
local listing assets/metadata, while image labels still come from repodata.
--github-data accepts a saved {"owner/repo": {"topics": [], "license": ...}}
snapshot for reproducible offline checks. API failures are errors, not failures
of a repository's topic/license checks.
"""

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request

from generate import version_key

DEFAULT_REPODATA = "https://platypuschan.github.io/ns8-modules/ns8/updates/repodata.json"
CATEGORIES = set("collaboration communication core database development documentation "
                 "monitoring multimedia office security storage system_administration web".split())
PNG = b"\x89PNG\r\n\x1a\n"


def read_json(location, headers=None):
    if str(location).startswith("https://"):
        request = urllib.request.Request(str(location), headers=headers or {})
        with urllib.request.urlopen(request, timeout=35) as response:
            return json.load(response)
    return json.loads(Path(location).read_text(encoding="utf-8"))


def displayed_version(entry):
    versions = [(version_key(v["tag"]), v) for v in entry.get("versions", [])]
    versions = [(key, v) for key, v in versions if key is not None]
    stable = [(key, v) for key, v in versions if key[3] == 1]
    return max(stable or versions, key=lambda item: item[0])[1] if versions else {}


def checks(entry, repository):
    description = entry.get("description", {})
    docs = entry.get("docs", {})
    categories = entry.get("categories", [])
    return {
        "topic": "ns8" in (repository.get("topics") or []),
        "categories": bool(categories) and all(c in CATEGORIES for c in categories),
        "logo": bool(entry.get("logo")),
        "screenshots": bool(entry.get("screenshots")),
        "description": len(description.get("en", "")) >= 60,
        "translations": len(description) > 1,
        "docs": bool(docs.get("documentation_url")) and bool(docs.get("bug_url")),
        "min_core": bool(displayed_version(entry).get("labels", {}).get("org.nethserver.min-core")),
        "license": bool(repository.get("license")),
    }


def local_entries(directory, published):
    by_id = {entry["id"]: entry for entry in published}
    entries = []
    for path in sorted(directory.glob("*/metadata.json")):
        entry = read_json(path)
        entry["id"] = path.parent.name
        # Do not count a filename alone as a usable local image.
        logo = path.parent / "logo.png"
        entry["logo"] = logo.is_file() and logo.read_bytes().startswith(PNG)
        entry["screenshots"] = [p.name for p in sorted((path.parent / "screenshots").glob("*.png"))
                                if p.read_bytes().startswith(PNG)]
        entry["versions"] = by_id.get(entry["id"], {}).get("versions", [])
        entries.append(entry)
    if not entries:
        raise ValueError(f"No app metadata found in {directory}")
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repodata", default=DEFAULT_REPODATA)
    parser.add_argument("--apps", type=Path)
    parser.add_argument("--github-data", type=Path)
    args = parser.parse_args()
    entries = read_json(args.repodata)
    if not entries:
        raise ValueError("Empty published catalog")
    if args.apps:
        entries = local_entries(args.apps, entries)
    snapshot = read_json(args.github_data) if args.github_data else None
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ns8-modules-quality-check"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    failures = 0
    for entry in entries:
        url = urllib.parse.urlsplit(entry.get("docs", {}).get("code_url", ""))
        parts = url.path.strip("/").split("/")
        if url.hostname != "github.com" or len(parts) != 2:
            raise ValueError(f"Unsupported source repository URL for {entry['id']}")
        repo = "/".join(parts)
        repository = snapshot[repo] if snapshot is not None else read_json(f"https://api.github.com/repos/{repo}", headers)
        result = checks(entry, repository)
        missing = [name for name, passed in result.items() if not passed]
        failures += bool(missing)
        version = displayed_version(entry).get("tag", "no release")
        print(f"{entry['id']}: {sum(result.values())}/9 ({version}); missing: {', '.join(missing) or 'none'}")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Quality audit failed: {error}", file=sys.stderr)
        sys.exit(2)

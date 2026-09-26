#!/usr/bin/env python3
"""Build a static NethServer 8 repository from public GHCR module images."""

import argparse
import html
import json
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
ACCEPT = ", ".join(
    (
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    )
)


def version_key(tag):
    match = SEMVER.fullmatch(tag)
    if not match:
        return None
    major, minor, patch = (int(value) for value in match.group(1, 2, 3))
    prerelease = match.group(4)
    if prerelease is None:
        return (major, minor, patch, 1, ())
    identifiers = prerelease.split(".")
    if any(item.isdigit() and len(item) > 1 and item.startswith("0") for item in identifiers):
        return None
    parts = tuple((0, int(item)) if item.isdigit() else (1, item) for item in identifiers)
    return (major, minor, patch, 0, parts)


class Registry:
    def __init__(self, image):
        if not image.startswith("ghcr.io/"):
            raise ValueError(f"Expected a ghcr.io image: {image}")
        self.name = image.removeprefix("ghcr.io/")
        parameters = urllib.parse.urlencode(
            {"scope": f"repository:{self.name}:pull", "service": "ghcr.io"}
        )
        token = self.get_json(f"https://ghcr.io/token?{parameters}")["token"]
        self.headers = {"Authorization": f"Bearer {token}", "Accept": ACCEPT}

    @staticmethod
    def get_json(url, headers=None):
        request = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(request, timeout=35) as response:
            return json.load(response)

    def fetch(self, path):
        return self.get_json(f"https://ghcr.io/v2/{self.name}/{path}", self.headers)

    def tags(self):
        # list-tags works for images without a :latest tag.
        return self.fetch("tags/list").get("tags") or []

    def labels(self, tag):
        manifest = self.fetch(f"manifests/{urllib.parse.quote(tag)}")
        if "manifests" in manifest:
            candidates = manifest["manifests"]
            linux = [m for m in candidates if m.get("platform", {}).get("os") == "linux"]
            amd64 = [m for m in linux if m.get("platform", {}).get("architecture") == "amd64"]
            chosen = (amd64 or linux or candidates)[0]
            manifest = self.fetch(f"manifests/{chosen['digest']}")
        config = self.fetch(f"blobs/{manifest['config']['digest']}")
        return config.get("config", {}).get("Labels") or {}


def build(apps_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for directory in sorted(apps_dir.iterdir()):
        if not directory.is_dir():
            continue
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        image = metadata["source"]
        registry = Registry(image)
        candidates = [tag for tag in registry.tags() if version_key(tag) is not None]
        stable = sorted(
            (tag for tag in candidates if version_key(tag)[3] == 1),
            key=version_key,
            reverse=True,
        )
        testing = sorted(
            (tag for tag in candidates if version_key(tag)[3] == 0),
            key=version_key,
            reverse=True,
        )
        selected = testing[:1] + stable[:1]
        if not selected:
            print(f"SKIP {directory.name}: {image} has no SemVer release", file=sys.stderr)
            continue

        versions = []
        for tag in selected:
            versions.append(
                {
                    "tag": tag,
                    "testing": version_key(tag)[3] == 0,
                    "labels": registry.labels(tag),
                }
            )
        entry = {
            "id": directory.name,
            "name": metadata["name"],
            "description": metadata["description"],
            "logo": "logo.png",
            "screenshots": [
                f"screenshots/{file.name}"
                for file in sorted((directory / "screenshots").glob("*.png"))
            ] if (directory / "screenshots").is_dir() else [],
            "categories": metadata["categories"],
            "authors": metadata["authors"],
            "docs": metadata["docs"],
            "source": image,
            "versions": versions,
        }
        logo = directory / "logo.png"
        if logo.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Invalid PNG logo: {logo}")
        destination = output_dir / directory.name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(directory, destination)
        entries.append(entry)
        print(f"ADD  {directory.name}: {', '.join(selected)}")

    if not entries:
        raise RuntimeError("No released module images found; refusing to publish an empty catalog")
    (output_dir / "repodata.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    cards = []
    for entry in entries:
        title = html.escape(entry["name"])
        summary = html.escape(entry["description"].get("en", ""))
        version = html.escape(entry["versions"][-1]["tag"])
        code_url = html.escape(entry["docs"]["code_url"], quote=True)
        logo = html.escape(f"ns8/updates/{entry['id']}/logo.png", quote=True)
        cards.append(
            f'<article><img src="{logo}" alt="" width="64" height="64">'
            f'<h2><a href="{code_url}">{title}</a></h2>'
            f'<p>{summary}</p><small>Released version: {version}</small></article>'
        )
    page = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Platypuschan modules for NethServer 8</title>
<style>
body{font:1rem/1.55 system-ui,sans-serif;max-width:980px;margin:2rem auto;padding:0 1rem;color:#17212b}
a{color:#075e9c}code{overflow-wrap:anywhere;background:#edf3f7;padding:.15rem .35rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:1rem}
article{border:1px solid #cbd6de;border-radius:.7rem;padding:1.2rem}
article img{object-fit:contain;float:right}h2{font-size:1.2rem;margin:.1rem 0 .7rem}
small{color:#445663}
</style>
<main><h1>NS8 modules by Platypuschan</h1>
<p>Add this test catalog in <strong>Settings → Software repositories</strong>:</p>
<p><code>https://platypuschan.github.io/ns8-modules/ns8/updates/</code></p>
<p>Enable it and reload repositories in Software Center. These community test
modules are not certified by NethServer. Report issues through each module's
source repository.</p><div class="grid">""" + "".join(cards) + """</div>
<p><a href="ns8/updates/repodata.json">NS8 repository metadata</a></p>
</main></html>
"""
    output_dir.parent.parent.joinpath("index.html").write_text(page, encoding="utf-8")
    return entries


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apps", type=Path, default=Path("apps"))
    parser.add_argument("--output", type=Path, default=Path("site/ns8/updates"))
    args = parser.parse_args()
    try:
        build(args.apps, args.output)
    except (OSError, ValueError, KeyError, IndexError, urllib.error.URLError) as error:
        parser.exit(1, f"Catalog generation failed: {error}\n")

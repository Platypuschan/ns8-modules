# NS8 catalog quality review — 2026-10-17

Scope: the eight apps in `apps/` at catalog commit `ab365514f629df7979265a4d2052769da91a46b2`. No other repositories are in scope.

Criteria: [stephdl/ns8-apps](https://github.com/stephdl/ns8-apps#quality-score), checked against its README and `crawler/model.py` on 2026-10-17. The nine checks measure listing completeness, not runtime/security quality.

| App | Initial score | Missing initially | Prepared listing + existing released image | Minimum core change |
| --- | --- | --- | --- | --- |
| adguard-home | 6/9 | ns8 topic, screenshots, minimum core | 8/9 | 3.23.0 |
| fail2ban-reworked | 7/9 | ns8 topic, screenshots | 9/9 | already present |
| gitea-reworked | 7/9 | ns8 topic, screenshots | 9/9 | already present |
| maubot | 5/9 | ns8 topic, screenshots, minimum core, English description <60 characters | 8/9 | 3.23.0 |
| ntfy-reworked | 6/9 | ns8 topic, screenshots, minimum core | 8/9 | 3.22.0 |
| obsidian-livesync | 6/9 | ns8 topic, screenshots, minimum core | 8/9 | 3.22.0 |
| organizr-reworked | 7/9 | ns8 topic, screenshots | 9/9 | already present |
| samba-reworked | 7/9 | ns8 topic, screenshots | 9/9 | already present |

## Changes and publication boundaries

- Added and read back the `ns8` GitHub topic on all eight source repositories. This change is already public. Existing licenses are recognized as GPL-3.0; none were changed.
- Standard categories, PNG logos, translated descriptions and documentation/issue links already passed.
- Added screenshots to catalog app directories. Seven apps use unchanged screenshots from real Debian 13 QEMU installation artifacts for their current source commit. Status screenshots containing loading skeletons were omitted.
- Samba uses a browser capture of the actual remote-domain setup wizard, with example data and a mocked read-only domain lookup in a local preview. This is a UI preview, not evidence of an NS8 installation or AD join.
- Extended the maubot English description in the catalog and source UI metadata.
- Four module PRs add `org.nethserver.min-core` and increment `CATALOG_VERSION`: AdGuard Home 0.1.2, maubot 0.1.2, ntfy 0.3.5, Obsidian LiveSync 0.3.1. The minimums conservatively match cores recorded by existing successful QEMU installation tests; older versions were not compatibility-tested. No label is fabricated in the catalog for an old image.

The prepared metadata/assets meet all listing checks under this repository’s control. The four image-label points remain pending merge and a new tested stable module release. Screenshots and the catalog description require merging the catalog PR and its Pages publish job. A later stephdl crawl (documented interval: up to six hours) is needed to reflect the public changes. No merge, stable release or Pages deployment was performed by this task.

## Source and screenshot evidence

Exact source commits, artifact IDs, run links and screenshot SHA-256 values are in [quality-evidence-2026-10-17.json](quality-evidence-2026-10-17.json). These are dated observations, not a claim that a new run has passed. GitHub artifacts may expire; the committed screenshots remain available.

| App | Source commit | Screenshot source |
| --- | --- | --- |
| adguard-home | [ce4dc08c](https://github.com/Platypuschan/ns8-adguard-home/commit/ce4dc08cfe6c7228f70181dea16be5c9d55804d8) | [test run](https://github.com/Platypuschan/ns8-adguard-home/actions/runs/38154896956) |
| fail2ban-reworked | [52147df8](https://github.com/Platypuschan/ns8-fail2ban-reworked/commit/52147df83622d297579fb0e3919551b3fa744a4f) | [test run](https://github.com/Platypuschan/ns8-fail2ban-reworked/actions/runs/37212657944) |
| gitea-reworked | [5a82a748](https://github.com/Platypuschan/ns8-gitea-reworked/commit/5a82a748c886389990d153ffe8cf3078c059dd66) | [test run](https://github.com/Platypuschan/ns8-gitea-reworked/actions/runs/37219549922) |
| maubot | [814617bd](https://github.com/Platypuschan/ns8-maubot/commit/814617bd3491a6a45a6ce339b011304908d58d22) | [test run](https://github.com/Platypuschan/ns8-maubot/actions/runs/38081654839) |
| ntfy-reworked | [a7bea4a3](https://github.com/Platypuschan/ns8-ntfy-reworked/commit/a7bea4a347518ccdb5505639ac81f876d981c419) | [test run](https://github.com/Platypuschan/ns8-ntfy-reworked/actions/runs/37214325103) |
| obsidian-livesync | [d395bf03](https://github.com/Platypuschan/ns8-obsidian-livesync/commit/d395bf03744ce71242efb701eea5248808c99d77) | [test run](https://github.com/Platypuschan/ns8-obsidian-livesync/actions/runs/37245993463) |
| organizr-reworked | [c0cbfd1e](https://github.com/Platypuschan/ns8-organizr-reworked/commit/c0cbfd1e7cbbc1951a50d85dbcf6c38b2fb780bc) | [test run](https://github.com/Platypuschan/ns8-organizr-reworked/actions/runs/37214330747) |
| samba-reworked | [314ae53c](https://github.com/Platypuschan/ns8-samba-reworked/commit/314ae53c84d275762be7a3c7496cc634fd51ba44) | Local browser preview of the overlay wizard and upstream UI 3.5.0 |

## Reproduce the audit

From this repository on a workstation with Python 3:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check-quality.py
python3 scripts/check-quality.py --apps apps
```

The default audits the public catalog, including the selected stable image labels (or the highest testing version if no stable exists). `--apps apps` overlays local metadata/assets but still uses actual published image labels. Neither mode predicts labels for an unreleased image. Exit 0 means 9/9 for every entry, exit 1 means criteria are missing, exit 2 means the audit could not complete (for example an API failure).

For a saved catalog and GitHub snapshot:

```sh
python3 scripts/check-quality.py --repodata /path/to/repodata.json --apps apps --github-data /path/to/github-data.json
```

The GitHub snapshot maps `owner/repo` to the public repository object with `topics` and `license`. Optional `GH_TOKEN` or `GITHUB_TOKEN` avoids low unauthenticated API limits.

## Validation

- Four audit regression tests plus the actual catalog metadata/assets check.
- Catalog generation fetched public GHCR versions and labels for all eight modules; copied asset paths and PNG signatures checked locally.
- All four changed modules: shell syntax, catalog-version consistency against `origin/main`, whitespace checks.
- Existing module unit suites: AdGuard Home 34, maubot 35, ntfy 38, Obsidian LiveSync 50; all passed using Python 3.13 with PyYAML 6.0.3 and ldap3 2.9.1.
- Current PR CI and exact head commits are recorded in the linked PRs and the final agent-exchange handoff. No live user-system tests were performed.

## Module pull requests

- [AdGuard Home #3](https://github.com/Platypuschan/ns8-adguard-home/pull/3)
- [maubot #3](https://github.com/Platypuschan/ns8-maubot/pull/3)
- [ntfy #21](https://github.com/Platypuschan/ns8-ntfy-reworked/pull/21)
- [Obsidian LiveSync #4](https://github.com/Platypuschan/ns8-obsidian-livesync/pull/4)

---
name: file-license
description: Create or update LICENSE files and third-party attribution. Pre-stored texts for MIT, Apache-2.0, BSD-2/3-Clause, ISC, Unlicense. Covers license selection, SPDX IDs, and compliance.
updated: 2026-06-12
---

# License Create

## 1§ Purpose
Produce a correct, GitHub-detectable `LICENSE` file and the required third-party
attribution documents. Output is plain text — never markdown-formatted.

GitHub license detection fuzzy-matches the file against canonical SPDX texts and
requires ≥90% similarity. Any wrapper text, formatting, or custom annotation in the
LICENSE file body reduces the match score and causes detection to fail.

## 2§ Use when
- A project has no `LICENSE` file or has one with incorrect formatting.
- User asks "which license should I use?", "add a license", or "Lizenz erstellen".
- A new version of the project requires updating the copyright year.
- Third-party dependencies need attribution documentation.

## 3§ Hard constraints
- Filename: `LICENSE` — no extension, at the project root. GitHub recognizes
  `LICENSE`, `LICENSE.md`, `LICENSE.txt`, and `COPYING`; plain `LICENSE` has
  the highest detection reliability.
- File content: plain text only. No markdown headers, no links, no commentary
  anywhere in the file body. The entire file must be the canonical license text.
- Canonical text only: load from `assets/` for pre-stored licenses. Never
  paraphrase, reorder, or annotate the license body.
- `YEAR` and `FULLNAME` are the only fields to fill (MIT, ISC, BSD variants).
  Never leave them unfilled. Ask the user if unknown.
- For licenses not pre-stored: fetch from the SPDX canonical URL listed in §5.
  Verify the fetched content matches the SPDX expected text before writing.
- SPDX identifier: after writing `LICENSE`, add the SPDX ID to all package
  manifests that have a `license` field (`package.json`, Cargo.toml `[package]`,
  `pyproject.toml [tool.poetry]`/`[project]`, `go.mod` comment).

## 4§ Decision gate
Work through these questions in order. Stop at the first match.

1. Commercial only, source not to be shared → no open source license; add a
   proprietary notice: `Copyright (c) YEAR COMPANY. All rights reserved.`
2. Non-commercial or ShareAlike required → `CC-BY-NC-SA-4.0` (creative/app
   work) or `AGPL-3.0-only` (software, all uses must share source)
3. SaaS / network use must trigger source sharing → `AGPL-3.0-only`
4. All derivative software must be open source → `GPL-3.0-only`
5. Library: modifications to the library open, but linking is allowed → `LGPL-3.0-only`
6. File-level copyleft: modified files open, rest can be proprietary → `MPL-2.0`
7. Need patent protection in addition to copyright → `Apache-2.0`
8. Maximum simplicity, most ecosystems → `MIT`
9. Minimal text, npm default → `ISC`
10. Public domain for software → `Unlicense`
11. Public domain for data or content → `CC0-1.0`

Default for new open source software: `MIT`.

## 5§ License catalog

| SPDX ID | Fill fields | Badge color | Storage |
|---|---|---|---|
| `MIT` | YEAR, FULLNAME | `green` | `assets/mit.txt` |
| `Apache-2.0` | none | `blue` | Fetch: `https://spdx.org/licenses/Apache-2.0.txt` |
| `BSD-2-Clause` | YEAR, FULLNAME | `blue` | `assets/bsd-2-clause.txt` |
| `BSD-3-Clause` | YEAR, FULLNAME | `blue` | `assets/bsd-3-clause.txt` |
| `ISC` | YEAR, FULLNAME | `green` | `assets/isc.txt` |
| `Unlicense` | none | `lightgrey` | `assets/unlicense.txt` |
| `GPL-3.0-only` | none | `red` | Fetch: `https://spdx.org/licenses/GPL-3.0-only.txt` |
| `LGPL-3.0-only` | none | `orange` | Fetch: `https://spdx.org/licenses/LGPL-3.0-only.txt` |
| `LGPL-2.1-only` | none | `orange` | Fetch: `https://spdx.org/licenses/LGPL-2.1-only.txt` |
| `AGPL-3.0-only` | none | `red` | Fetch: `https://spdx.org/licenses/AGPL-3.0-only.txt` |
| `MPL-2.0` | none | `orange` | Fetch: `https://spdx.org/licenses/MPL-2.0.txt` |
| `CC0-1.0` | none | `lightgrey` | Fetch: `https://spdx.org/licenses/CC0-1.0.txt` |
| `CC-BY-4.0` | none | `blue` | Fetch: `https://spdx.org/licenses/CC-BY-4.0.txt` |
| `CC-BY-NC-SA-4.0` | none | `purple` | Fetch: `https://spdx.org/licenses/CC-BY-NC-SA-4.0.txt` |

All pre-stored texts are the canonical SPDX versions. They do not change within
a version number. Apache 2.0 has been unchanged since 2004; MIT since OSI
approval in 1999. Do not re-fetch pre-stored texts unless the user reports a
GitHub detection failure.

Shields.io badge format (`for-the-badge` style):
```markdown
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
```

## 6§ Third-party license compliance

Third-party compliance is a legal requirement in distributed software, not
an optional good practice.

### 6.1§ What each license requires from users

| Their license | Your obligation when distributing |
|---|---|
| MIT, ISC | Preserve their copyright notice and license text in any binary or bundle |
| BSD-2-Clause | Same as MIT |
| BSD-3-Clause | Same as BSD-2; also: do not use their name to endorse your product |
| Apache-2.0 | Include their NOTICE file if they provide one; preserve copyright, patent, and trademark notices; note any file modifications |
| GPL-2.0/3.0 | Your entire distributed work becomes GPL; provide full source code |
| LGPL-2.1/3.0 | Library source for modifications; larger work can be proprietary |
| AGPL-3.0 | Same as GPL but also triggered by users interacting via a network |
| MPL-2.0 | Modified MPL files must stay MPL; rest of the project may use another license |
| CC licenses | Attribution required; ShareAlike requires same license on derivatives |

### 6.2§ Attribution file conventions
Use one convention per project consistently:

`THIRD_PARTY_LICENSES.md` — Markdown, readable on GitHub, recommended for web/app projects.
See `assets/third-party-licenses.template.md` for the format.

`NOTICES` — plain text, Apache-style, preferred for Apache-2.0 licensed projects or
CLI tools distributed as binaries.

### 6.3§ Automation — run these via Claude's tools
Do not ask the user to run these manually:

| Ecosystem | Tool | Command |
|---|---|---|
| npm / Node | `license-checker` | `npx license-checker --json > third-party.json` |
| Rust / Cargo | `cargo-license` | `cargo license --json` |
| Python | `pip-licenses` | `pip-licenses --format=json` |
| Multi-language | `LicenseFinder` | `license_finder report` |

### 6.4§ When to create an attribution file
Always create when:
- Any dependency uses Apache-2.0 (NOTICE file may be required by upstream)
- Any dependency uses GPL/LGPL/AGPL (source obligations apply to the full project)
- The project is distributed as a compiled binary or bundled package
- Any dependency license is other than MIT, ISC, or BSD

### 6.5§ License compatibility
Combining code with incompatible licenses creates a legal conflict:
- Permissive (MIT, BSD, ISC, Apache-2.0) → can be combined with almost anything
- Apache-2.0 → compatible with GPL-3.0, incompatible with GPL-2.0
- GPL-3.0 → incoming MIT/Apache code is fine; the combined work is GPL-3.0
- GPL code in a proprietary project → forbidden
- LGPL → proprietary code can link to the library; modifications to the library must be open

## 7§ Workflow
1. Ask: copyright holder (full legal name or organization), year, project type
   (library, app, SaaS, data). If the project has a package manifest, read it first
   to check for an existing `license` field.
2. Apply §4 decision gate to select or confirm the license.
3. Load the pre-stored text from `assets/`, or fetch from the SPDX URL (§5).
   Fill `YEAR` and `FULLNAME` where required. Verify no other text is altered.
4. Write `LICENSE` to the project root. Plain text, no extension.
5. Add the SPDX identifier to package manifests.
6. Check third-party compliance (§6):
   a. Read package manifests for dependency lists.
   b. Run the ecosystem tool via Claude's tools to get license data.
   c. If attribution is required: create or update `THIRD_PARTY_LICENSES.md`
      using `assets/third-party-licenses.template.md`.
7. Deliver: `LICENSE`, updated manifests, `THIRD_PARTY_LICENSES.md` if applicable.
   Report: license chosen (SPDX ID), fill fields used, third-party licenses
   found and actions taken.

## 8§ Output contract
Must include:
- `LICENSE` at project root — plain text, no extension, exact canonical text
- `YEAR` and `FULLNAME` filled where the license requires them
- SPDX identifier in package manifests
- `THIRD_PARTY_LICENSES.md` when any dependency requires attribution

Must not include:
- Markdown, HTML, or any formatting inside the `LICENSE` file body
- Modified or paraphrased license text
- Unfilled `YEAR` or `FULLNAME` in the delivered file
- Two licenses in one `LICENSE` file — use `LICENSE-MIT` + `LICENSE-APACHE`
  for dual-licensing, and state the dual-license in `README.md`

## 9§ Associated documents
Stored assets only — licenses marked Fetch in 5§ are retrieved from their SPDX
URLs at runtime and are intentionally not stored here.
- [assets/mit.txt] — MIT License (YEAR, FULLNAME)
- [assets/bsd-2-clause.txt] — BSD 2-Clause License (YEAR, FULLNAME)
- [assets/bsd-3-clause.txt] — BSD 3-Clause License (YEAR, FULLNAME)
- [assets/isc.txt] — ISC License (YEAR, FULLNAME)
- [assets/unlicense.txt] — The Unlicense (no fill fields)
- [assets/third-party-licenses.template.md] — THIRD_PARTY_LICENSES.md template

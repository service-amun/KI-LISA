---
name: file-readme
description: Create or update README.md files following GitHub conventions. Produces human-facing, visually structured project documentation. Supports multilingual output via separate language files.
updated: 2026-06-14
---

# Readme Create

## 1§ Purpose
Produce a complete README.md that serves as the project's first impression on
GitHub. Output is human-facing — written for a developer unfamiliar with the
project, optimized for readability, scannability, and visual appeal.

Note: READMEs are prose documents for humans. Do not apply harness internal
markdown conventions (no-bold, no-italic, N§ sections). Follow GitHub README
conventions instead.

## 2§ Use when
- A project has no README or has a stub that needs fleshing out.
- An existing README is stale, poorly structured, or missing key sections.
- A multilingual README variant is needed.
- User says "write the README", "create README", or "README erstellen".

## 3§ Hard constraints
- Read project context first: CLAUDE.md, package files (`package.json`,
  `pyproject.toml`, `Cargo.toml`, `go.mod`), existing README, any `docs/`
  folder, repository description.
- Never omit badges because the GitHub remote is unknown. Delivered badge URLs
  must always resolve: when the remote is unknown, use only static shields.io
  badges with hardcoded values (`https://img.shields.io/badge/label-value-color`).
  Never place any placeholder — neither `<USER>/<REPO>` nor literal `USER/REPO` —
  inside a delivered badge URL. List the dynamic GitHub badge URLs (with
  `USER/REPO` to substitute) in the response text for post-publish replacement.
- No unfilled content fields. If critical prose information (project name,
  license, tagline) is missing, ask before writing.
- Target length: 500–1,500 words. Over 2,000 words: split into `docs/`.
- Use GitHub-Flavored Markdown (GFM) features throughout — not vanilla Markdown.
- Badges and dynamic visual elements: include the toolkit in §6 by default. Omit an
  individual element only when its required URL or info is genuinely unavailable — then list
  its dynamic URL in the response text for post-publish substitution (same rule as badges).
  Keep the core badge row meaningful and lean (build, license, version, downloads, plus
  stars/forks/issues where useful); max 4 per row, group related badges. Showcase cards
  (stats, streak, trophy, visitor counter, quote) belong on profile/org/showcase READMEs
  (§4), not on lean software-repo READMEs.
- Zero-setup only: every dynamic element in §6 renders from a URL alone — no GitHub Action,
  no third-party account, no paid service. Never introduce an element that needs a workflow,
  a login, or money.
- Multiple languages: separate files only (`README.de.md`). Never mix languages
  in one file via collapsible sections.
- Order chapters by reader relevance, not authoring convenience: what the reader
  needs first comes first — what is it, what do I get, how do I start in seconds,
  details on demand. Never open with internal mechanics. Canonical order in §5.
- Content boundary — internal mechanics belong in PROJECT.md, never in the README:
  configuration load order, lifecycle, data flow, build internals. The README may
  show one architecture DIAGRAM in the hero when it sells the project at a glance,
  but never narrates internals in prose and never makes them a chapter.
- Inventory sections (what's included, components, parts lists): one line per
  element — name plus a single short clause. Long per-element descriptions,
  reference tables, and full detail go to PROJECT.md or the artifact's own index.
- Instructions win on simplicity — the fewest, most automated steps that work.
  Prefer a single command. Give one default install path; collapse alternative
  scopes (global / project / partial) into a `<details>` block, never three full blocks.
- Contributing is opt-in only: include a short Contributing section solely when a
  `CONTRIBUTING.md` exists to link. Otherwise omit it entirely — never a default chapter.
- Never put non-code in a code environment. Reserve fenced code blocks and inline
  backticks for actual code: commands, source, file names, paths, field names, and literal
  config values. A natural-language instruction or a prompt to paste into Claude is NOT code —
  render it as a blockquote, not a fenced block (paths inside it may still be backticked).
  Prose, labels, and descriptions never go in code formatting.
- Never merge distinct element categories into one table or row to save space: each
  category is its own section, and each element its own row, even when a category holds
  a single element. One-element categories (an output style, a base UI) get their own
  table — never folded together because each is small.
- Sort inventory elements by a single explicit order — alphabetical by name unless a
  stronger order exists (lifecycle order for hooks, dependency order for a pipeline).
  Never leave an inventory in arbitrary insertion order.
- Install paths are subsections under ONE Installation section, never separate top-level
  sections: a console quick start (one command set) and a manual path for non-console users
  (download, extract, copy by hand) live as `###` subsections inside the same Installation
  section. They share the parent so the reader sees one place to get started, two ways in.
- Every major section is collapsible, uniform, and open by default: wrap each in
  `<details open>` — including nested sub-blocks — so nothing is hidden on load while the
  reader can still collapse what they do not need. All section headers use the identical
  summary markup; no section keeps a different format or stays a plain heading. A short
  inline link row can stand in for a table of contents.
- The disclosure arrow must sit in line with the header text: the summary uses an INLINE
  heading-style label — `<summary><b><font size="5">🎯&nbsp; Title</font></b></summary>` —
  never a block heading (`<summary><h2>…</h2></summary>`), which pushes the ▶ marker onto its
  own line above the text. Give every collapsible section an `<a id="…">` anchor above it so
  the link row resolves.
- A hero diagram must encode real content — actual components, counts, and real flow of this
  project — never a generic abstract graph that would fit any project unchanged. It visualizes
  the project in descending order of reader relevance, mirroring the chapter order (§5):
  primary is what you get (the contents and their scale); secondary is how it works (the
  load/wiring model); tertiary is how to install. The most relevant layer is the visual focus;
  install is the most de-emphasized node, never the entry the diagram is built around.

## 4§ README type variants
The template (`assets/readme.template.md`) targets a software repository — the
default case. Profile and organization READMEs differ structurally:

- Profile README (`<username>/<username>` repo): omit quick start, usage, and
  contributing; replace value proposition with a personal bio; use a centered
  header with avatar; keep it short (≤400 words). Add showcase elements from the §6
  dynamic toolkit — stats and top-languages card, streak, trophy, social/contact badges,
  visitor counter, optional dev-quote card — as a few accents, not all at once.
- Organization README (`<org>/.github` repo): replace personal bio with mission
  and team overview; link to key repos, docs, and contribution guide; no quick
  start section.

When producing profile or org READMEs: use the template as a structural
starting point, remove inapplicable sections, and adjust content per the notes
above.

## 5§ Content standard

Order every chapter by reader relevance. The sequence below is the canonical order
for a software or tool repository — what the reader needs first comes first. Omit any
section the project does not need; never lift internal-interest content above
reader-interest content.

Canonical order:
1. Visual header — animated banner (capsule-render) or centered logo block
2. Language selector — only when multilingual (see §7)
3. Badges — build, license, version; max 4 per row
4. Tagline — one sentence: what the project is and who it is for
5. Demo or visual — screenshot, GIF, or one architecture diagram, within the first
   visible viewport. For tools without a UI: a Mermaid diagram or a terminal block
6. Value proposition — 2–3 sentences: what is it, who is it for, why use it
7. What you get — the project's value as an inventory: a features list, or for a
   catalog/toolkit repo the included parts. One line per element (§3 inventory rule);
   per-element depth lives in PROJECT.md
8. Installation — one section holding both ways to get started as `###` subsections: a
   console quick start (fewest, most automated steps) and a manual path for non-console
   users (download, extract, copy by hand). Alternative scopes and partial install collapse
   into nested `<details>` blocks
9. Usage — one real example from the actual project
10. License — name and link, one line
11. Footer wave — capsule-render footer in the same color scheme as the header

Never a chapter: internal load order, lifecycle, or build mechanics — these go to
PROJECT.md (§3 content boundary). Contributing only when a `CONTRIBUTING.md` exists
to link (§3).

Optional (add when applicable):
- Table of contents — for READMEs over 1,000 words; prefer a collapsible `<details>` block (§6)
- Call-to-action link row under the tagline — Explore docs / View Demo / Report Bug / Request Feature (§6)
- Back-to-top links after each major section (§6)
- Tech stack — logo badge row or skill-icon strip (§6)
- Project traction — star-history chart and contributors image, software repos only (§6)
- Prerequisites — only when non-obvious or frequently missed
- Troubleshooting / FAQ — use `<details>` to keep page length manageable
- Acknowledgments
- Support section — for open-source projects distributed publicly: a `## 💛 Support`
  section placed before Contributing; include a GitHub star badge and a Ko-fi
  donation link when the author has provided those URLs. Use `?style=social` for
  the star badge and the Ko-fi `githubbutton_sm.svg` button. Also add both to the
  header `<div align="center">` block after the main badge row. Never invent URLs;
  only include when the author has provided them.

Installation section — include whenever the project is something users install or
deploy, not just a library they add as a dependency. Required for: CLI tools,
configuration harnesses, scaffolding kits, desktop apps. Cover all relevant
install paths (global vs. project scope, partial installs). If scopes differ
meaningfully (e.g. user-level vs. project-level), give each a named subsection.
Always include a "verify it works" step after installation.

## 6§ Visual standard

Animated header — capsule-render (https://capsule-render.vercel.app):
Place as the very first element in the README. Choose wave type and a color
gradient that suits the project's identity. Parameters:
```markdown
![header](https://capsule-render.vercel.app/api?type=waving&color=0:HEX1,100:HEX2&height=200&section=header&text=Project%20Name&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=36&desc=Short%20tagline%20here&descSize=17&descAlignY=54&descColor=e0e7ff)
```
Available types: `waving`, `wave`, `egg`, `shark`, `slice`, `rect`, `rounded`,
`soft`, `cylinder`, `blur`, `transparent`. Animation options: `fadeIn`,
`scaleIn`, `blink`, `twinkling`.

Footer wave — mirror color order, `section=footer`, no text:
```markdown
![footer](https://capsule-render.vercel.app/api?type=waving&color=0:HEX2,100:HEX1&height=120&section=footer)
```

Centered badge block — place inside `<div align="center">` after the header:
```html
<div align="center">

[English](README.md) | [Deutsch](README.de.md)

![Version](https://img.shields.io/badge/version-1.0.0-4f46e5?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-7c3aed?style=for-the-badge)
![Build](https://img.shields.io/github/actions/workflow/status/USER/REPO/ci.yml?style=for-the-badge)

One-line bold tagline.

</div>
```

Badge style — use `for-the-badge` for the main badge row; bold and clear.
Static fallbacks when GitHub remote is not yet set:
```markdown
![Version](https://img.shields.io/badge/version-0.1.0-4f46e5?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-7c3aed?style=for-the-badge)
```
Dynamic GitHub badges (replace after publishing):
```markdown
![Release](https://img.shields.io/github/v/release/USER/REPO?style=for-the-badge)
![Build](https://img.shields.io/github/actions/workflow/status/USER/REPO/ci.yml?style=for-the-badge)
```

Emoji in section headings — use one emoji per `##` heading to aid scanning.
Pick domain-appropriate icons; keep the same emoji across all translations:
```markdown
## ⚙️ Architecture
## 📦 What's included
## 🚀 Quick start
## 🔧 Adapting
## 🤝 Contributing
## 📄 License
```
Do not use emoji in body text or bullet points — section headings only.

Dark/light mode images — when supplying separate image assets for each mode:
```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
  <img alt="Project logo" src="assets/logo-light.png" width="400">
</picture>
```
capsule-render SVGs render acceptably in both modes without this technique.

GFM alerts — use instead of bold warnings or ALL CAPS:
```markdown
> [!NOTE]
> Background context or supplementary information.

> [!TIP]
> Best practices or time-saving suggestions.

> [!IMPORTANT]
> Critical information users must not miss.

> [!WARNING]
> Potential problems or breaking changes.

> [!CAUTION]
> Actions that could cause data loss.
```

Collapsible sections — for FAQ, detailed install options, changelogs:
```html
<details>
<summary>Advanced configuration</summary>

Content here. Blank line after </summary> is required for Markdown to render.

</details>
```

Mermaid diagrams — for architecture, decision flows, or tool overviews when
no screenshot is available. Load the `mermaid` skill for full styling guidance
(color system, shape semantics, classDef, themeVariables). Requirement: at least
3 distinct node shapes and 3 semantic color classes. The diagram must encode this
project's real content — its actual components, counts, and flow — never a generic
session→config graph that would fit any project unchanged. Order its layers by reader
relevance, mirroring the chapter order: primary is what you get (contents and scale),
secondary is how it works (load/wiring), tertiary is how to install (a single
de-emphasized node). Verify it renders before delivery (visual-verify rule); reserved
Mermaid keywords (`style`, `end`, `class`, `default`) are invalid node ids.

Code blocks — always specify language. Never use bare fences.

Dynamic toolkit — zero-setup showcase elements. Every URL below renders from parameters
alone: no GitHub Action, no account, no cost. They are third-party SVG endpoints and can
rate-limit or change — use them as accents, never as the only source of critical information,
and pick a `theme=` matching the header gradient. Substitute `USER`, `REPO`, `PACKAGE` after
publishing; omit any element whose URL or info is unavailable.

Tech-stack badges (one logo per technology) and a skill-icon strip:
```markdown
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)

[![Stack](https://skillicons.dev/icons?i=react,ts,node,python,docker)](https://skillicons.dev)
```

Social and contact badges — link each to its destination; omit any without a URL:
```markdown
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](LINKEDIN_URL)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](YOUTUBE_URL)
```

Dynamic repo badges — social proof, auto-updating once the remote exists:
```markdown
![Stars](https://img.shields.io/github/stars/USER/REPO?style=social)
![Forks](https://img.shields.io/github/forks/USER/REPO?style=social)
![Issues](https://img.shields.io/github/issues/USER/REPO)
![Last commit](https://img.shields.io/github/last-commit/USER/REPO)
```
Registry version and downloads — pick the matching ecosystem:
```markdown
![npm version](https://img.shields.io/npm/v/PACKAGE)
![npm downloads](https://img.shields.io/npm/dm/PACKAGE)
![PyPI version](https://img.shields.io/pypi/v/PACKAGE)
![PyPI downloads](https://img.shields.io/pypi/dm/PACKAGE)
```

Visitor counter — profile/showcase, no account:
```markdown
![Profile views](https://komarev.com/ghpvc/?username=USER&style=for-the-badge)
```

Showcase stat cards — profile/org READMEs only; set `theme=` to match the palette:
```markdown
![Stats](https://github-readme-stats.vercel.app/api?username=USER&show_icons=true&theme=THEME)
![Top languages](https://github-readme-stats.vercel.app/api/top-langs/?username=USER&layout=compact&theme=THEME)
![Streak](https://streak-stats.demolab.com/?user=USER&theme=THEME)
![Trophies](https://github-profile-trophy.vercel.app/?username=USER&theme=THEME)
```

Project traction — software repos:
```markdown
[![Star history](https://api.star-history.com/svg?repos=USER/REPO&type=Date)](https://star-history.com/#USER/REPO&Date)

![Contributors](https://contrib.rocks/image?repo=USER/REPO)
```

Dev-quote card — optional accent, profile/showcase:
```markdown
![Quote](https://quotes-github-readme.vercel.app/api?type=horizontal&theme=THEME)
```

Back-to-top links — set an anchor at the very top, then link back after each major section:
```markdown
<a id="readme-top"></a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>
```

Collapsible table of contents — for READMEs over ~1,000 words:
```markdown
<details>
<summary>Table of Contents</summary>

- [What is it](#what-is-it)
- [Quick start](#quick-start)
- [Usage](#usage)

</details>
```

Call-to-action link row — place under the tagline; omit any link without a destination:
```markdown
[Explore the docs »](DOCS_URL)

[View Demo](DEMO_URL) · [Report Bug](ISSUES_URL) · [Request Feature](ISSUES_URL)
```

Image gallery — multiple screenshots side by side via an HTML table:
```html
<table>
  <tr>
    <td><img src="assets/shot-1.png" alt="Screen 1" width="400"></td>
    <td><img src="assets/shot-2.png" alt="Screen 2" width="400"></td>
  </tr>
</table>
```

## 7§ Multi-language workflow
1. Establish the primary language (default: English) — this is `README.md`.
2. Name additional files using ISO 639-1 codes:
   `README.de.md`, `README.fr.md`, `README.ja.md`, `README.zh-CN.md`.
3. Add a language selector at the very top of every language file:
   ```markdown
   [English](README.md) | [Deutsch](README.de.md) | [Français](README.fr.md)
   ```
4. Each language file is complete and self-contained.
5. In the primary README, note which translations are maintained and whether
   they may lag behind the primary — place the note directly under the language
   selector line.
6. Produce the primary language file first, then additional language files.

## 8§ Workflow
1. Load `assets/readme.template.md`. For profile or org READMEs: apply §4 variant notes.
2. Read all available project context.
3. Identify missing information. Ask for any critical missing fields
   (project name, license, tagline) before proceeding. Badge URLs can always
   use static fallbacks — do not block on missing GitHub remote URL.
4. Choose a color scheme for the header gradient. Pick colors that fit the
   project's identity or domain. Build the capsule-render URL for both header
   and footer (§6).
5. Fill the template section by section. Remove inapplicable optional sections.
   Strip all HTML comments from the final output.
6. Apply visual standard (§6): animated header, badge block in centered div,
   emoji section headings, GFM alerts where appropriate, collapsible sections
   for lengthy content, footer wave.
7. For tool READMEs without a UI screenshot: place the architecture diagram or
   a representative code block immediately after the badge block.
8. For multilingual output: follow §7, produce primary file first.
9. Deliver the completed file(s). State which static badges should be replaced
   with dynamic GitHub URLs after publishing, and which assets (screenshots,
   logos) still need to be provided.

## 9§ Output contract
Must include:
- All required sections from §5 in order
- At least one GFM feature (alert, collapsible, or mermaid diagram)
- Language selector at top if multilingual
- No HTML comments in the delivered file
- Code blocks with language identifiers throughout

Must not include:
- Non-code in a code environment — prompts, instructions, prose, or labels in fenced blocks
  or inline backticks (a prompt to paste is a blockquote; backtick only commands/paths/code)
- A section that is not collapsible, not open by default, or uses a different header format
- A block heading (`<h2>`) inside a `<summary>` — breaks the inline disclosure arrow
- Unfilled `<PLACEHOLDER>` fields
- More than 4 badges in a single row
- Multiple languages in one file
- Showcase/stat cards on a lean software-repo README — reserve them for profile/org/showcase (§4)
- Any element requiring a GitHub Action, a third-party account, or a paid service
- Harness-internal conventions (N§ sections, no-bold rule)

## 10§ Associated documents
- [assets/readme.template.md] — README template (default: repository; adapt for profile/org per §4)

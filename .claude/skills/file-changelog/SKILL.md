---
name: file-changelog
description: Create, update, or audit CHANGELOG.md files following Keep a Changelog 1.1.0 and Semantic Versioning. Covers init, adding entries, cutting releases, and migrating non-standard formats.
updated: 2026-06-14
---

# Changelog Create

## 1§ Purpose
Produce and maintain a `CHANGELOG.md` that communicates user-facing changes clearly.
Standard: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/). Versions
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The file lives
at the project root.

Note: changelogs are prose documents for humans, not machines. They are curated
summaries, not git log dumps. Do not apply harness internal markdown conventions
(N§ sections, no-bold). Follow changelog conventions instead.

## 2§ Use when
- A project has no `CHANGELOG.md` or has a stub.
- New work is ready to be documented in [Unreleased].
- A release is being cut and [Unreleased] should become a versioned entry.
- An existing changelog uses a non-standard format and needs migration.
- User says "update changelog", "add to changelog", "release schneiden", "CHANGELOG erstellen".

## 3§ Hard constraints
- Never write a raw git log dump — always curate for user-facing relevance.
- Dates: ISO 8601 only — `YYYY-MM-DD`.
- Version headers: `[MAJOR.MINOR.PATCH]` — no `v` prefix inside the brackets.
- Always include an `[Unreleased]` section at the top.
- Only write non-empty category sections per release entry. Keep exactly one section per
  category — never two `### Changed` blocks in the same entry.
- `[Unreleased]` records the net delta since the last release, not the development journey.
  When a later change supersedes an earlier `[Unreleased]` entry — a rename, removal, or merge
  of something added in the same unreleased cycle — rewrite the affected entry to the net
  result instead of appending the reversal. An artifact added and then removed before any
  release nets to nothing and belongs in no section. Describe everything by its final name and
  final state; intermediate names and in-cycle rewrites are not changelog content.
- Verify the current version in the project's version source (`Cargo.toml`,
  `package.json`, `pyproject.toml`, `go.mod`) before writing version numbers.
- Automation note: for projects using Conventional Commits, [git-cliff](https://git-cliff.org/)
  can generate entries automatically. This skill covers manual authoring; automation
  is out of scope but not precluded.

## 4§ Decision gate

| Mode | When | Action |
|---|---|---|
| Init | No `CHANGELOG.md` exists | Create from `assets/changelog.template.md`; fill project name and repo URL |
| Add entry | User describes one or more changes to record | Append bullets to the correct [Unreleased] category |
| Release cut | User says "release X.Y.Z" or "version bump" | Rename [Unreleased] → [X.Y.Z] - DATE; open fresh [Unreleased]; update diff links |
| Audit / migrate | Existing file is non-standard or stale | Reformat per §5; preserve all historical data; flag non-user-facing entries before removing |

## 5§ Format spec

File header:

```markdown
# Changelog

All notable changes to <PROJECT_NAME> are documented here.
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

Version entry structure:

```markdown
## [Unreleased]

## [1.2.3] - 2026-06-11

### Security
- Fix XSS vulnerability in comment rendering

### Added
- Add dark mode support

### Changed
- **Breaking:** Remove /api/v1 endpoint — migrate to /api/v2 (see [migration guide](url))
- Improve search response time by 40%

### Deprecated
- Deprecate `--legacy-mode` flag; will be removed in 2.0.0

### Removed
- Remove CSV export (use the new XLSX export instead)

### Fixed
- Fix crash when uploading files over 5 GB
```

Version diff links at file bottom:

```markdown
[Unreleased]: https://github.com/<USER>/<REPO>/compare/v1.2.3...HEAD
[1.2.3]: https://github.com/<USER>/<REPO>/compare/v1.2.2...v1.2.3
[1.2.2]: https://github.com/<USER>/<REPO>/releases/tag/v1.2.2
```

Ordering and formatting rules:
- Versions: newest first, oldest last.
- Category order within a version: Security, Added, Changed, Deprecated, Removed, Fixed.
- Omit empty category sections entirely.
- Breaking changes: prefix with `**Breaking:**` and link to a migration guide.
- PR or issue references: optional — append `([#123](url))` at end of entry line.
- Diff links are optional and tag-dependent: add `compare/<tag>` and `releases/tag/<tag>`
  links only when those git tags or releases actually exist — the URLs 404 until the tag
  is pushed. A repo with no tagged releases yet ships no diff links. Monorepos without
  per-component tags: omit them or link to a commit range.

## 6§ Content standard

Six standard categories — use exactly these names, casing, and order:

| Category | Include |
|---|---|
| Security | Vulnerability patches of any severity — always use this section, never bury in Fixed |
| Added | New features, new options, new endpoints, new integrations |
| Changed | Modified behavior a user would notice; breaking changes with `**Breaking:**` prefix |
| Deprecated | Features still present but scheduled for removal; include target removal version or date |
| Removed | Features that no longer exist; include migration path if one exists |
| Fixed | Bug fixes that affected real users |

Include (user-facing):
- New capabilities and UI changes
- API or interface changes
- Performance improvements measurable by users
- Any fix a user would have noticed as broken

Exclude (not user-facing):
- Internal refactors with no observable effect
- Dependency version bumps (exception: security-related bumps go in Security)
- Dev tooling, CI/CD, dotfile changes
- Test-only changes
- Code style or formatting changes

## 7§ Writing style
- Audience: users of the software, not developers of the codebase.
- Voice: imperative present tense — "Add X", "Fix Y", "Remove Z".
- Specificity: one concrete detail per entry — "Fix crash on upload > 5 GB", not "Fix crash".
- Length: one line per entry; merge related commits into one logical bullet.
- No raw commit messages, no internal file paths, no module names.
- Breaking changes: `**Breaking:** <what changed>. Migrate by <how> — see [migration guide](url).`
- Deprecations: `Deprecate <feature>; will be removed in <version or date>. Use <alternative> instead.`

## 8§ Workflow
1. Read existing `CHANGELOG.md` if present. Identify mode (§4).
2. Check the project's version source for the current version number.
3. Init: load `assets/changelog.template.md`. Fill `<PROJECT_NAME>` and repo URL.
   Remove the example version block if no releases exist yet.
4. Add entry: identify the correct category. Before appending, scan [Unreleased] for an
   entry the new change supersedes (same artifact renamed, removed, or merged within this
   unreleased cycle) and collapse it to the net result rather than adding a contradicting
   line. Then append the bullet. Apply writing style (§7). If the category section does not
   exist yet, add it in the order defined in §5.
5. Release cut: confirm version string with user. Move [Unreleased] content to a
   new versioned section with today's date. Add a fresh empty [Unreleased]. Update
   the diff links block at the file bottom — add a line for the new version,
   update the [Unreleased] diff base.
6. Audit / migrate: reformat entry by entry per §5. Preserve all dates and version
   numbers. Flag entries that appear non-user-facing and confirm removal before
   deleting them.
7. Deliver the updated file. State what was added, changed, or migrated.

## 9§ Output contract
Must include:
- File at project root: `CHANGELOG.md`
- File header with project name and semver link
- `[Unreleased]` section at top
- Version entries newest-first, ISO 8601 dates
- Non-empty category sections only, in the order from §5
- Version diff links only when matching git tags or releases exist — omit them for an
  untagged repo, where they would 404

Must not include:
- Raw git log output or commit hashes as entry text
- Internal module names, file paths, or developer-only details
- Empty category sections
- `v` prefix inside version brackets
- Changes that are not user-facing

## 10§ Associated documents
- [assets/changelog.template.md] — `CHANGELOG.md` template for init mode

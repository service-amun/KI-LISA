---
name: mage-notes-project
description: Product spec and architecture decisions for MaGe Notes — a local-first note-taking desktop app.
updated: 2026-06-11
---

# MaGe Notes — Project Spec

## 1§ Goal

Single-user, offline-first note-taking app for Windows. Notes are Markdown, stored
locally in plain files. No cloud sync, no accounts — data travels with the machine.

## 2§ Core features

- Note list: flat collection of Markdown files in a single configurable folder.
- Editor: split view (Markdown source left, rendered preview right); live sync.
- Search: full-text search over note content and titles; instant results on keypress.
- Tags: extracted from YAML frontmatter (`tags:` field); filter panel in sidebar.
- Export: single note as PDF via system print dialog; no other export formats.
- Settings: editor font size, theme (Dark / Light), notes folder path.
- Persistent window state: size, position, last-open note.

## 3§ Non-goals

- Cloud sync or multi-device support — local file system only.
- Real-time collaboration — single-user, no conflict resolution.
- Mobile (iOS, Android) — Windows desktop only.
- Note hierarchy / notebooks — flat folder, no nesting. Folders as notebooks is
  a common feature request; excluded because tags + search make it unnecessary
  and hierarchies complicate the file-watch model.
- In-app auto-update — distributed as NSIS installer; new versions require manual
  download and install.

## 4§ Directory structure

```text
mage-notes/
  shell/                  — Tauri app shell; owns window, IPC commands, file I/O
    src/                  — SolidJS frontend; all UI components and state
    src-tauri/            — Rust backend; Tauri commands, file-watch plugin
      src/
        lib.rs            — command registration and plugin init
        commands.rs       — all Tauri commands (load_notes, save_note, etc.)
  data/                   — runtime data folder (next to exe in installed builds)
```

## 5§ Architecture decisions

### 5.1§ Plain files as the data store

Notes live as individual `.md` files in a user-chosen folder. No database,
no proprietary format.

Rationale: plain files survive the app — users can edit notes with any editor,
version them with git, or move them between machines without tooling. A SQLite
store would be faster for search but would opaque the data and create a migration
burden on every schema change.

### 5.2§ Frontend-managed search index

Search is implemented as an in-memory index built at startup from file content.
No external search library — plain `Map<filename, tokens[]>` with TF-IDF scoring.

Rationale: the expected note count is under 10 000 files and < 500 MB total. At
that scale an in-memory index rebuilds in < 2 s and avoids the complexity of an
embedded search engine. Re-evaluated if perf profiling shows rebuild time > 5 s.

### 5.3§ File watcher drives UI state (locked)

The Tauri file-watch plugin (`tauri-plugin-fs-watch`) is the single source of
truth for note list changes. The frontend never mutates the note list directly —
it only responds to `fs:changed` events from the watcher.

Rationale: external edits (user saving from VS Code, git checkout) must reflect
immediately. Any direct-mutation model creates a split-brain between app state
and disk state. Locked because all save/load paths depend on this invariant.

### 5.4§ YAML frontmatter for metadata

Tags, title override, and creation date are stored as YAML frontmatter at the
top of each note. No sidecar files, no external metadata store.

Rationale: keeps the file self-contained. Sidecars can desync when files are
moved or renamed outside the app. The frontmatter is standard Markdown
convention and readable by other tools.

### 5.5§ No APP_MANIFEST.json

App identity (`productName`, `version`) lives in `tauri.conf.json` and
`Cargo.toml`. No separate manifest file.

Rationale: two places are already one too many. A third manifest diverges.

## 6§ Domain vocabulary

- Note — a single `.md` file in the notes folder, not a database row. "Open note"
  means the file is loaded into the editor, not locked or checked out.
- Notes folder — the one user-configured directory the app watches. There is no
  concept of multiple libraries or workspaces.

## 7§ Invariants and gotchas

- Invariant: the file watcher is the only writer to note-list state — if any code
  mutates the list directly, app state and disk state split-brain and the UI shows
  stale notes until restart.
- Gotcha: frontmatter is parsed only at file-load time, not on every keypress —
  editing `tags:` in the source pane does not refresh the tag filter until the note
  is saved and re-read. Trigger a reload after save, never poll.

## 8§ AI pitfalls

- Claude tends to add a SQLite/cache layer for search "for performance" — do not.
  Search is an in-memory rebuild by design (§5.2); a persistent index reintroduces
  the migration burden plain files were chosen to avoid.
- Claude tends to write to the note list after a save — never. Saving writes the
  file; the watcher emits `fs:changed` and the list updates from that event (§5.3).

## 9§ Constraints and external dependencies

- Windows 10/11 x64 only — uses `tauri-plugin-fs-watch` (Windows ReadDirectoryChangesW).
- Requires WebView2 runtime (bundled bootstrapper in installer).
- Note folder must be on a local drive — network shares are untested and not supported.
- PDF export uses the system print dialog via `window.print()` — no headless renderer.

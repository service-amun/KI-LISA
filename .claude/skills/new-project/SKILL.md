---
name: new-project
description: Scaffold a new Claude Code project — directory structure, desktop shortcut, and delegation to native skills per document. For projects under ~/.claude/projects/ or nested in a project.
updated: 2026-06-12
---

# Project New

## 1§ Purpose
Create a complete, ready-to-use project folder by orchestrating the harness's
existing skills. Each document is produced by the skill that owns it. This skill
handles only what no other skill covers: directory structure, desktop shortcut,
and `.gitignore`.

Projects nest arbitrarily — each project's `.claude/projects/` holds child
projects of identical structure.

## 2§ Use when
- User wants to create a new Claude Code project.
- User wants to add a nested sub-project inside an existing project.
- User requests a standard project scaffold.

## 3§ Hard constraints
- Never create a project without confirming the name with the user first.
- Never create a desktop shortcut without explicit yes/no confirmation.
- Never overwrite an existing directory — stop and report if the target path exists.
- Always delegate document creation to the owning skill — never write README,
  CHANGELOG, LICENSE, CLAUDE.local.md, or settings files directly.

## 4§ Decision rules
- Parent directory not specified: use `$HOME/.claude/projects/` as default.
- CWD is inside `<project>/.claude/projects/`: offer that path as parent; confirm.
- Desktop shortcut declined: skip silently, do not re-ask.
- Windows: use WScript.Shell COM object to create a `.lnk` file on the Desktop.
- macOS/Linux: create a symlink in `~/Desktop/` if that directory exists.

## 5§ Workflow
1. Confirm the project name. Derive a filesystem-safe slug (lowercase, spaces to
   hyphens, no special characters). Display name and slug may differ.
2. Determine parent directory: check CWD or default to `$HOME/.claude/projects/`.
   Confirm the full target path `<parent>/<slug>/` before proceeding.
3. Verify the target path does not exist; stop and report if it does.
4. Ask: "Create a desktop shortcut? (yes/no)"
5. Create the directory tree via PowerShell (Windows) or Bash (macOS/Linux):
   ```text
   <slug>/
   ├── .claude/
   │   ├── projects/
   │   ├── rules/
   │   │   └── rules.index.toon    ← direct (empty index, header row only)
   │   ├── skills/
   │   │   └── skills.index.toon   ← direct (empty index, header row only)
   │   ├── agents/
   │   │   └── agents.index.toon   ← direct (empty index, header row only)
   │   └── settings.local.json     ← settings skill
   ├── CLAUDE.local.md              ← file-claude skill
   ├── .gitignore                   ← direct (Claude git knowledge)
   ├── LICENSE                      ← file-license skill
   ├── README.md                    ← file-readme skill
   ├── README.de.md                 ← file-readme skill
   ├── CHANGELOG.md                 ← file-changelog skill
   └── PROJECT.md                   ← file-project skill
   ```
6. Write directly (no skill needed):
   - `.gitignore` — write from git knowledge; include standard Node/Python/OS ignores plus `.claude/settings.local.json` and `CLAUDE.local.md`.
   - Three empty TOON index files — write each with a `#` descriptor comment and a
     header row only; no data rows; no trailing newline (TOON spec):
     ```toon
     # Rules index. TOON format: header row of field names separated by " | ", one rule per subsequent row.
     name | description
     ```
     ```toon
     # Skills index. TOON format: header row of field names separated by " | ", one skill per subsequent row.
     name | description
     ```
     ```toon
     # Agents index. TOON format: header row of field names separated by " | ", one agent per subsequent row.
     name | description
     ```
7. Invoke skills in order — each produces its file into the new project root.
   Invoke `file-claude` after the index files exist so it detects the directories and
   adds discovery and maintenance instructions automatically:
   - `settings`: create `.claude/settings.local.json` with empty permissions.
   - `file-claude`: produce `CLAUDE.local.md` using the file-claude template; file name
     is `CLAUDE.local.md`, not `CLAUDE.md`.
   - `file-license`: produce `LICENSE` (ask copyright holder name).
   - `file-readme`: produce `README.md` and `README.de.md`.
   - `file-changelog`: produce `CHANGELOG.md` with a `[0.1.0]` initial entry.
   - `file-project`: produce `PROJECT.md` (create mode; minimal for a fresh scaffold).
8. If desktop shortcut confirmed, run the platform snippet from §5.1.
9. Report: print the full created tree and shortcut path (if created). Note which
   index files were created and that discovery instructions were added to CLAUDE.local.md.

### 5.1§ Desktop shortcut snippets
Windows (PowerShell):
```powershell
$target  = "<ABSOLUTE_PROJECT_PATH>"
$lnkPath = "$env:USERPROFILE\Desktop\<SLUG>.lnk"
$shell   = New-Object -ComObject WScript.Shell
$lnk     = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath       = $target
$lnk.WorkingDirectory = $target
$lnk.Description      = "<PROJECT_NAME> — Claude Code project"
$lnk.Save()
```

macOS/Linux (Bash):
```bash
ln -s "<ABSOLUTE_PROJECT_PATH>" "$HOME/Desktop/<SLUG>"
```

## 6§ Output contract
Must include:
- Complete directory tree from §5 step 5
- Three empty TOON index files with descriptor comment and header row only
- All documents produced by their owning skills
- `.gitignore` written from git knowledge
- User confirmation before any desktop shortcut
- Summary listing every created path

Must not include:
- Directly written README, CHANGELOG, LICENSE, PROJECT.md, or settings content (delegate to skills)
- Desktop shortcuts without explicit confirmation
- Data rows in the empty index files — header row only at scaffold time

## 7§ Associated documents
- [assets/new-project.example.md] — example of a completed scaffold

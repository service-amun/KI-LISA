---
description: Git commit and branch conventions for this project.
alwaysApply: true
---

# Git Workflow

## 1§ Scope
Applies to all git operations in this repository: commits, branches, pushes,
and pull requests. Does not cover code review process — see [docs/review.md].

## 2§ Rules
- Use Conventional Commits format: `type(scope): description`
  (e.g. `fix(auth): handle expired tokens`).
- Keep the subject line under 72 characters; use the body for context and
  motivation, not for listing what changed.
- Reference issues in the commit body when one exists: `Fixes #123`.
- Never commit directly to `main` or `master`; work on a feature branch.
- Require explicit user confirmation before running `git push` or
  `git push --force`.

## 3§ Preferred patterns
- `fix:` over `chore:` when a change corrects observed wrong behavior, even
  if minor — the type signals intent to reviewers and changelog generators.
- One logical change per commit over bundled multi-concern commits — split with
  `git add -p` when needed.

## 4§ Avoid
- Commit messages like "wip", "fix stuff", "update", or "changes" — use the
  type prefix; these messages are useless in changelogs and `git bisect`.
- `git commit --amend` on commits already pushed to a shared branch — creates
  history conflicts for other contributors.
- `--no-verify` to bypass hooks — investigate the hook failure instead.

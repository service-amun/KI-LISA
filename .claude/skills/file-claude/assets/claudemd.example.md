# MyProject

## 1§ Commands
- `npm test` — full test suite (Jest, ~45 s); run before any commit
- `npm run build` — TypeScript compilation to `dist/`; must succeed before deploy
- `npm run lint` — ESLint; auto-fixable with `npm run lint:fix`
- `npm run format` — Prettier; run after any manual whitespace change

## 2§ Architecture
- `src/api/` — Express route handlers; one file per resource, no business logic here
- `src/services/` — all business logic; services are the only callers of `src/db/`
- `src/db/` — Drizzle ORM queries; no raw SQL outside this directory
- `src/types/` — shared TypeScript interfaces and enums; no runtime code

## 3§ Code conventions
- 2-space indentation (enforced by `.editorconfig`; do not change)
- `async/await` over Promise chains — no `.then()` chains in new code
- Throw `AppError` instances (from `src/types/errors.ts`), never plain `Error`
- All exported functions require explicit return type annotations

## 4§ Workflow
- Branch from `main`; prefix: `feat/`, `fix/`, `chore/`
- Squash-merge only — no merge commits on `main`
- PRs require one reviewer approval; CI must be green before merge

## 5§ Gotchas
- `DB_URL` must be set in `.env.local`; no fallback — app crashes silently without it
- Integration tests require a running Postgres container: `docker compose up -d db`
- Test database is seeded by `npm run db:seed:test`; re-run after schema migrations

## 6§ Available rules
Rules in `.claude/rules/` load on demand — read before editing matching files:
- `api-style.md` — REST design conventions (load when editing `src/api/`)
- `testing.md` — test structure and assertion style (load when editing tests)
- `db-conventions.md` — Drizzle query patterns and migration workflow

## 7§ Available skills
Skills live in `.claude/skills/`. Before invoking one, read
`.claude/skills/skills.index.toon` — TOON format, first non-comment line is a
header row (`name | description`), one skill per subsequent line. Load the full
`skills/<name>/SKILL.md` only when the skill is needed.

## 8§ Verification
- After any service change: `npm test` — zero failures required
- After any schema change: `npm run db:migrate && npm run db:seed:test`
- After any API change: `npm run build` to catch type errors before review

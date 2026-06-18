---
name: tasks
description: Guide to Claude Code's two task systems: work board (TaskCreate/TaskUpdate) and background execution (Bash + TaskOutput). Decision framework, patterns, anti-patterns, and dependency design.
updated: 2026-06-12
---

# Tasks

## 1§ Purpose
Produce correct, efficient task workflows in Claude Code — managing a structured work
board of named tasks with dependencies, running work in the background while continuing
foreground work, or coordinating multiple subagents against a shared task list.

## 2§ Use when
- 3 or more distinct, trackable steps in a session
- Parallel independent work across subagents
- Long-running background execution (builds, scans, research) alongside foreground work
- Cross-session continuity — tasks that survive context resets and compaction
- User says "track", "plan", "background", "parallel tasks", or mentions TaskCreate/TaskList

Do not use for 1–2 trivial steps, conversational responses, or anything completable without
status tracking — the coordination overhead exceeds the value.

## 3§ Hard constraints
- Never read background task output with `Read` or `Bash tail`/`cat`. Use `TaskOutput`
  exclusively. Every `Read`/`tail` call injects the full output into the context window,
  causing rapid context bloat — a documented anti-pattern (issue #44957).
- Never pass a work-board task ID (from `TaskCreate`) to `TaskOutput` or `TaskStop`.
  These tools operate on a separate namespace (background shell/agent execution IDs).
  Mixing IDs fails silently or with a confusing error.
- Never call `TaskUpdate(status: "completed")` before verifying actual output. Declaration
  is not completion.
- Claim ownership immediately: call `TaskUpdate(owner: ...)` before starting work,
  never after.
- Capture background task IDs at launch — there is no tool to enumerate running background
  processes. A lost ID is permanently unrecoverable.
- Always call `TaskList` before `TaskCreate` to check for duplicates.

## 4§ System separation
Claude Code has two task systems that share confusing naming. They do not interact.

| System | Purpose | ID source | Tools |
|---|---|---|---|
| Work board | Named tasks — status, owner, dependencies | `TaskCreate` result | `TaskCreate`, `TaskUpdate`, `TaskGet`, `TaskList` |
| Background execution | Async shell commands and agents | `Bash {run_in_background: true}` result | `TaskOutput`, `TaskStop` |

`TaskOutput` and `TaskStop` belong to background execution only — they have no effect on
work board tasks. `TaskCreate`/`TaskUpdate`/`TaskGet`/`TaskList` have no effect on
background execution.

## 5§ Decision framework

Use the work board when:
- 3+ steps that benefit from status tracking or resumability after compaction
- Multiple subagents need to claim independent items without race conditions
- The task list should survive context resets via `CLAUDE_CODE_TASK_LIST_ID`

Use background execution when:
- A long-running shell command (build, install, scan) should not block ongoing work
- Results can be consumed later and do not need immediate blocking

Skip tasks entirely when:
- 1–2 trivial steps with no parallelism
- Single-response or conversational output

Granularity: aim for 5–6 tasks per agent. Finer creates coordination overhead that
exceeds the work; coarser produces long runs without check-ins and increases wasted effort.

## 6§ Task quality
Three fields, each serves a different consumer:

| Field | Consumer | Pattern |
|---|---|---|
| `subject` | List display | Short imperative: "Fix OAuth redirect loop in auth.ts" |
| `activeForm` | Spinner text while in_progress | Present continuous: "Fixing OAuth redirect loop" |
| `description` | Agent reading the task | Acceptance criteria + file paths + relevant context |

`description` is what subagents read to understand the task — include what "done" looks
like, specific file paths, and any constraints. "Fix auth bug" fails; "Fix the token-exchange
in `src/auth/oauth.ts:L47` — validate `state` before token exchange; passes when all
OAuth tests pass" works.

`activeForm` is almost never set but substantially improves UX — always include it.

## 7§ Work board workflow
1. Call `TaskList` — check for existing tasks and duplicates.
2. Plan the full task graph: identify all tasks, acceptance criteria, and dependency
   edges before creating any.
3. Call `TaskCreate` for each task. Set `subject`, `activeForm`, `description`. Record
   the returned task ID immediately from each `tool_result`.
4. Call `TaskUpdate` with `addBlockedBy` / `addBlocks` to encode all dependency edges.
5. For the first available (unblocked, unclaimed) task: call
   `TaskUpdate(status: "in_progress", owner: "<agent>")` immediately — do not delay.
6. Do the work. Verify output against the `description` acceptance criteria.
7. Call `TaskUpdate(status: "completed")` only after verification passes.
8. The next unblocked task auto-transitions from `blocked` to `pending` — no manual
   intervention needed. Return to step 5.
9. At session end: call `TaskUpdate(status: "deleted")` on all remaining completed tasks
   to trigger the cleanup pipeline and prevent accumulation.

## 8§ Background execution workflow
1. Launch: `Bash {command: "...", run_in_background: true}`. Capture the returned task ID
   immediately — store it explicitly. There is no recovery path for a lost ID.
2. Continue foreground work. Do not poll.
3. To check non-blocking: `TaskOutput(task_id: ID, block: false)` — returns immediately
   with current status and partial output.
4. To wait for result: `TaskOutput(task_id: ID, block: true, timeout: <ms>)` — blocks
   until done. Default timeout is 30 s; set explicitly for slow tasks (e.g. `120000`).
5. On completion: check `status` field. `completed` = done; `running` = still active;
   `failed` = error in `output`.
6. To cancel: `TaskStop(task_id: ID)` — kills the shell process.
7. Note: subagents cannot call `TaskStop` (issue #23154). If a subagent's background
   task hangs, the parent session must cancel it using the captured ID.

## 9§ Patterns
See [assets/task-patterns.md] for concrete, ready-to-adapt templates:
- Sequential task list (3–7 ordered tasks, chained deps)
- Orchestrator + workers (parallel dispatch with subagent prompt template)
- Background + foreground
- Cross-session shared task list (`CLAUDE_CODE_TASK_LIST_ID`)

## 10§ Dependency design
- `addBlockedBy: [id1, id2]` — this task waits until id1 and id2 reach `completed`.
- `addBlocks: [id3]` — when this task completes, id3 auto-transitions from `blocked`
  to `pending`. No manual intervention needed.
- Encode all dependency edges before any work starts — retrofitting edges after tasks
  are in_progress is error-prone.
- Design for maximum parallelism: add a blocker only when the dependency is genuine.
  Serializing independent tasks is the most common avoidable bottleneck.

## 11§ Task hygiene
- Call `TaskUpdate(status: "deleted")` on completed tasks at session end — triggers
  the cleanup pipeline in the `cleanup-sessions` hook.
- Cross-session lists: set `CLAUDE_CODE_TASK_LIST_ID=<name>` identically in all
  participating terminals. All sessions read and write the same board in real time.
- Named task lists do not auto-expire. Use `deleted` status when the project is done.
- Cleanup (harness `cleanup-sessions` hook): removes UUID-keyed task directories older
  than 14 days, and `.json` task files with `completed` or `deleted` status older than
  7 days. Task hygiene reduces this residual — it does not eliminate the need for cleanup.

## 12§ Hooks integration
Three task lifecycle hooks are available in `settings.json`:

| Hook event | Exit 2 effect | Use for |
|---|---|---|
| `TaskCreated` | Rejects creation; stdout sent as feedback | Naming conventions, duplicate detection |
| `TaskCompleted` | Blocks completion; stdout sent as feedback | Automated acceptance tests |
| `TeammateIdle` | Keeps teammate active; stdout sent as feedback | Checklist enforcement in agent teams |

Exit 0 = allow. Exit 2 = reject with stdout as feedback injected into Claude's context.
Configure these via a lifecycle hook.

## 13§ Output contract
Must include:
- `TaskCreate` calls with `subject`, `activeForm`, `description` all populated
- Dependency edges encoded before any task starts
- Background task IDs captured and noted immediately at launch
- `TaskUpdate(owner: ...)` called before starting any task

Must not include:
- `Read` or `Bash tail`/`cat` on background task output files
- `TaskOutput`/`TaskStop` called with a work-board task ID
- `TaskUpdate(status: "completed")` before output verification
- `TaskCreate` without a prior `TaskList` check

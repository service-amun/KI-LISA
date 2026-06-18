---
name: loop
description: Claude Code loop setup and operation: /loop, CronCreate, and ScheduleWakeup. Decision framework, loop.md authoring, context hygiene, self-termination patterns, and platform caveats.
updated: 2026-06-12
---

# Loop

## 1§ Purpose
Design, launch, and safely operate Claude Code loops — choosing the right recurring-task
system, configuring cadence and stopping conditions, authoring `loop.md` override files,
and preventing context bloat and runaway iterations.

## 2§ Use when
- User asks to set up `/loop`, recurring tasks, or a scheduled prompt in an active session
- CI/CD watching, PR babysitting, deployment polling, or iterative background research
- Deciding between loop, Monitor, desktop scheduled task, and cloud routine
- Authoring or updating a `loop.md` override file
- User needs to understand why a loop is running, stuck, or consuming unexpected tokens

Do not use for:
- One-shot tasks — use Bash or a single Agent call
- Real-time stream observation where events arrive unpredictably — use Monitor instead
- Tasks that must survive machine shutdown — use cloud routines
- Non-interactive pipelines — set `CLAUDE_CODE_DISABLE_CRON=1` to block accidental scheduling

## 3§ Hard constraints
- Never rely on a session-scoped loop to survive session end. Cron tasks are in-memory only.
  They can be restored via `claude --resume` within 7 days, then vanish permanently.
- Always embed an explicit stopping condition in every loop prompt. The 7-day auto-expiry
  is a backstop, not a design feature — a loop with no stopping condition will run until it
  expires, draining tokens silently.
- Never poll background output with `Read`, `Bash tail`, or `Bash cat` between iterations.
  Each call injects the full output into context; use Monitor for streams and self-paced
  ScheduleWakeup for reasoning-based polling.
- Always specify scope limits in the loop prompt — what Claude is not allowed to touch.
  Without explicit exclusions, each iteration may take wider action than intended.
- `ScheduleWakeup` has no cancellation API (issue #58235). A running self-paced loop can
  only be stopped by pressing Esc or closing the session. Warn the user before launching.
- `loop.md` is silently ignored on Bedrock, Vertex AI, and Microsoft Foundry. Verify the
  provider before relying on a `loop.md` override.

## 4§ System comparison

| System | Needs open session | Survives machine off | Cadence | Best for |
|---|---|---|---|---|
| `/loop` (session) | Yes | No | Fixed or self-paced | CI watching, PR tending, iterative research |
| Desktop scheduled task | No | No | Cron expression | Nightly local jobs |
| Cloud routine | No | Yes | Cron expression | Fully autonomous background automation |
| Monitor | Yes | No | Event-driven | Log tailing, stream observation, file watching |

Decision rule:
- User will have an active session open → `/loop`
- Task must run overnight or survive session end → desktop task (machine must stay on) or cloud routine
- Trigger is a stream event, not a time interval → Monitor
- Cost matters and the trigger is irregular → Monitor (zero tokens between events vs fixed-interval loop burning tokens whether or not anything changed)

## 5§ Setup workflow
Use AskUserQuestion for the four decisions that determine the correct setup. Ask all questions
before composing any command.

Step 1 — determine system fit:
Call AskUserQuestion with header "Loop type" and question "Will you keep an active Claude Code
session open while this runs?" with options "Yes — I'll be at my machine with a session open"
and "No — I need it to run in the background or overnight". If the user answers "No": redirect
to a desktop scheduled task or cloud routine and exit this skill.

Step 2 — determine cadence:
Call AskUserQuestion with header "Cadence" and question "Should this run on a fixed schedule or
let Claude adjust the wait based on what it finds?" with options "Fixed interval — same gap every
time (e.g. every 5 minutes)" and "Self-paced — Claude adjusts the wait based on what it finds".

Step 3 — determine stopping condition:
Call AskUserQuestion with header "Stopping" and question "What stops this loop?" with options
"Explicit condition — a checkable state (e.g. CI is green, queue is empty)",
"Manual only — I'll press Esc or close the session when done", and
"Iteration limit — run a fixed number of times then stop".

Step 4 — offer loop.md persistence (only if the prompt is reusable):
If the prompt describes a recurring project-level or global maintenance task, call AskUserQuestion
with header "Persistence" and question "Should this be saved as loop.md so bare /loop always runs
it?" with options "Project scope — .claude/loop.md (this project only)",
"User scope — ~/.claude/loop.md (all projects)", and "No — one-off only".

Step 5 — compose and deliver:
- Self-paced: `/loop <prompt>`
- Fixed interval: `/loop <interval> <prompt>` (e.g. `/loop 5m check CI on PR #1234`)
- With `loop.md`: write the file using the template at [assets/loop.template.md], then instruct
  the user to run bare `/loop`

Always embed the stopping condition and scope limits in the final prompt, regardless of cadence.

## 6§ loop.md authoring
`loop.md` replaces the built-in maintenance prompt for bare `/loop` calls with no arguments.
Two locations, first match wins: `.claude/loop.md` (project) or `~/.claude/loop.md` (user).
Edits take effect on the next iteration. Max size: 25,000 bytes.

A complete `loop.md` has four parts:

1. Objective — one sentence: the goal and what success looks like
2. Scope — what Claude is allowed to touch; list explicit exclusions to prevent drift
3. Escalation — what to do when stuck, to prevent infinite retry on the same failure
4. Stopping condition — a check run at the start of each iteration; if met, do not reschedule

Use [assets/loop.template.md] as the starting point. Fill all four parts and strip comments
before saving.

Rules for effective `loop.md`:
- Concise: the file is read every iteration. Keep it under 200 lines.
- Unambiguous success state: "CI is green and all review threads are resolved" works;
  "improve code quality" does not.
- Explicit scope: "Allowed: `src/auth/` only. Not allowed: new PRs, dependency changes."
- Stopping instruction: "If conditions are met, output 'LOOP DONE' and do not call
  ScheduleWakeup." This is how self-paced loops terminate gracefully.

## 7§ Context and token hygiene
Session-scoped loops accumulate context across iterations. At approximately 83.5% context
capacity, compaction fires — the conversation is summarized and history is replaced by the
summary. State not written to files or tasks is lost at this point.

Rules for long-running loops:
- Write all loop state to a file (`_work/loop-state.md`) or the task work board before
  context reaches 70%.
- At each iteration start: read the state file first, then act, then update the state.
- Use TaskCreate/TaskUpdate to track items — the work board survives compaction and session
  restarts.
- Prefer Monitor for event-triggered work — zero tokens between events vs a fixed loop that
  checks even when nothing changed.

Token cost estimate: a self-paced iteration at 2,000 prompt tokens with a standard model costs
approximately 1 USD per 500 iterations. A `/loop 1m` loop running 8 hours fires ~480 times.
Set the interval no shorter than the task actually requires.

## 8§ Self-termination patterns
Three reliable mechanisms for loops that should stop on their own:

1. Prompt condition (self-paced only) — embed the check directly: "If all CI checks are green
   and there are no open review comments, output 'LOOP DONE' and do not call ScheduleWakeup."
   Claude ends the loop when the condition is met. Only works in self-paced mode — fixed-interval
   loops keep running regardless.

2. Task sentinel — create a TaskCreate entry before starting. Each iteration calls
   TaskUpdate(status: "completed") when done. The loop prompt reads TaskGet at the start of each
   iteration; if status is "completed", skip all work and do not reschedule.

3. File sentinel — write `_work/loop-done` when the condition is met. The loop prompt checks for
   the file first: "If `_work/loop-done` exists, do nothing and do not reschedule." Simple and
   survives compaction.

Recommendation: use self-paced mode + prompt condition for any loop with a natural end state.
Reserve fixed-interval for loops that truly have no stopping condition (dashboards, health
monitors) — and warn the user that they must press Esc manually.

## 9§ Platform caveats
- Bedrock / Vertex AI / Microsoft Foundry: `ScheduleWakeup` is unavailable. Self-paced `/loop`
  falls back to a fixed 10-minute interval, not user-configurable. `loop.md` is ignored and bare
  `/loop` shows the usage message.
- Disable loops in CI or pipeline contexts: set `CLAUDE_CODE_DISABLE_CRON=1` in the environment
  or in `settings.json` under `env`. This blocks all `CronCreate`, `CronList`, `CronDelete`, and
  `/loop` commands for the session.
- 7-day expiry: all session-scoped cron tasks expire after 7 days. `claude --resume` within 7 days
  restores them. After 7 days they are gone without warning — no notification, no error.

## 10§ Output contract
A valid loop setup produced by this skill must include:
- The exact `/loop` command or CronCreate call with the final prompt
- An explicit stopping condition in the prompt, or an acknowledgment that stop is manual-only
- Scope limits in the prompt
- `loop.md` written to the correct location if the user chose persistence
- A platform caveat note if the current provider is Bedrock, Vertex AI, or Foundry

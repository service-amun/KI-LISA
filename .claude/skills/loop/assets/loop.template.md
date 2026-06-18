<!-- Loop override template. Fill all four sections; strip all comments before saving.
     Location: .claude/loop.md (project-level) or ~/.claude/loop.md (user-level).
     This file is read every iteration — keep it under 200 lines. -->

<!-- OBJECTIVE: one sentence. State the goal and what a successful outcome looks like. -->
Check the `release/next` PR for CI failures and unresolved review comments. Success: CI is
green and all review threads are resolved.

<!-- SCOPE: list what Claude is allowed to touch. Explicit exclusions prevent drift across
     iterations as context accumulates. -->
Allowed: this repository's `release/next` branch, CI job logs, review comment threads.
Not allowed: opening new PRs, touching unrelated branches, modifying dependencies, pushing
to any branch other than `release/next`.

<!-- ESCALATION: define what to do when stuck. Without this, a recurring failure can cause
     Claude to attempt the same fix indefinitely. -->
If the same CI failure repeats 3 times without a new fix approach, post a summary comment
on the PR describing the error and stop attempting further fixes this iteration.

<!-- STOPPING CONDITION: this check runs at the start of every iteration. If the condition
     is met, Claude must not call ScheduleWakeup. This is the only way a self-paced loop
     terminates gracefully without user intervention. -->
If CI is green and all review threads are resolved, output "LOOP DONE: all conditions met"
and stop. Do not schedule another iteration.

# Task Patterns

Reference templates for the four common Claude Code task patterns.
Adapt field values; the structure is ready to use.

## 1§ Sequential task list

Use when: 3–7 ordered tasks where each step depends on the previous.

```text
# Step 1 — Create tasks
TaskCreate: subject="Read and understand codebase"
            activeForm="Reading codebase"
            description="Read CLAUDE.md, README.md, src/. Record: architecture, data flow,
                         entry points. Done when you can describe the data model without re-reading."
→ ID: T1

TaskCreate: subject="Identify problem areas"
            activeForm="Identifying problem areas"
            description="Based on codebase read: list files with complexity issues, missing tests,
                         or architectural concerns. Produce a prioritized list at _work/issues.md."
→ ID: T2

TaskCreate: subject="Fix top 3 issues"
            activeForm="Fixing issues"
            description="Apply targeted fixes to the top 3 items from _work/issues.md.
                         One commit per fix. Done when tests pass."
→ ID: T3

# Step 2 — Encode dependency chain
TaskUpdate: taskId=T2, addBlockedBy=[T1]
TaskUpdate: taskId=T3, addBlockedBy=[T2]

# Step 3 — Work through in order
# T1 is immediately available. T2 unblocks when T1 completes. T3 when T2 completes.
```

## 2§ Orchestrator + workers (parallel)

Use when: 3+ independent tasks with clear file boundaries and no shared state.

```text
# Step 1 — Create one task per independent unit (e.g. src/auth, src/api, src/db)
TaskCreate: subject="Audit src/auth"
            activeForm="Auditing src/auth"
            description="Read all files in src/auth/. List: functions, external deps,
                         test coverage gaps. Write summary to _work/audit-auth.md.
                         Done when _work/audit-auth.md exists and covers all files."
→ ID: T1

TaskCreate: subject="Audit src/api"
            activeForm="Auditing src/api"
            description="Read all files in src/api/. Same format as auth audit.
                         Write to _work/audit-api.md."
→ ID: T2

TaskCreate: subject="Audit src/db"
            activeForm="Auditing src/db"
            description="Read all files in src/db/. Write to _work/audit-db.md."
→ ID: T3

# No deps needed — all tasks are independent, all start immediately.

# Step 2 — Spawn one subagent per task. Use this prompt template:
"Your task ID is <ID>.
 1. Call TaskUpdate(taskId=<ID>, status='in_progress', owner='<agent-name>') immediately.
 2. <Task description verbatim from the description field>
 3. Verify your output meets the acceptance criteria in the description.
 4. Call TaskUpdate(taskId=<ID>, status='completed') only after verification."

# Step 3 — After all agents complete, synthesize _work/audit-*.md
```

## 3§ Background + foreground

Use when: a long-running shell command should not block ongoing implementation work.

```text
# Step 1 — Launch background task. Capture ID immediately.
Bash: command="npm test --coverage 2>&1", run_in_background=true
→ ID: BG1    ← store this; there is no way to recover it if lost

# Step 2 — Continue foreground work immediately (do not wait, do not poll with Read/tail)
# ... implement features, edit files ...

# Step 3 — Non-blocking status check at any point
TaskOutput: task_id=BG1, block=false
→ { status: "running" | "completed" | "failed", output: "...partial..." }

# Step 4 — Wait when the result is needed
TaskOutput: task_id=BG1, block=true, timeout=120000
→ { status: "completed", output: "Test results: 47 passed, 0 failed..." }

# Step 5 — Cancel if needed (from parent session; subagents cannot call TaskStop)
TaskStop: task_id=BG1
```

## 4§ Cross-session shared task list

Use when: multiple terminals or sessions should share one persistent task board.

```text
# Set CLAUDE_CODE_TASK_LIST_ID before launching claude in each terminal.
# All sessions with the same ID see and modify the same board in real time.

# PowerShell:
$env:CLAUDE_CODE_TASK_LIST_ID = "myproject"
claude

# Bash:
CLAUDE_CODE_TASK_LIST_ID=myproject claude

# Behaviour:
# — TaskCreate in session A → session B sees it via TaskList immediately
# — TaskUpdate in session B → session A sees the status change
# — Board persists on disk across session restarts and compaction
# — Named lists do not auto-expire: call TaskUpdate(status="deleted") when the project ends
```

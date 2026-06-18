# Mermaid Diagram Templates

One complete, runnable template per diagram type. Each shows the type's
characteristic syntax. Adapt data and labels; remove unused sections before
delivery. The flowchart template lives separately in [flowchart.template.md].

## 1§ Sequence — invocation / API flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#2FBF5E', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1E9447', 'lineColor': '#0D9488', 'fontSize': '14px'}}}%%
sequenceDiagram
    autonumber
    actor User
    participant Claude as 🤖 Claude Code
    participant Skill as 🛠️ Skill
    participant Hook as ⚡ Hook

    User->>+Claude: Request
    Claude->>+Skill: Load SKILL.md
    Skill-->>-Claude: Instructions
    Claude->>+Hook: PreToolUse
    Hook-->>-Claude: approved (exit 0)
    Claude-->>-User: Result
```

## 2§ State machine — lifecycle

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#2FBF5E', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1E9447', 'lineColor': '#0D9488', 'fontSize': '14px'}}}%%
stateDiagram-v2
    [*] --> Idle : init
    Idle --> Running : start
    Running --> Paused : pause
    Paused --> Running : resume
    Running --> Done : finish
    Running --> Failed : error
    Done --> [*]
    Failed --> [*]

    state Running {
        Executing --> Validating
        Validating --> Executing
    }
```

## 3§ Mindmap — feature taxonomy

```mermaid
mindmap
    root(("🧠 Harness"))
        Rules
            md-style
            json-style
            yaml-style
            toon-style
            command-execution
        Skills
            file-claude
            skills
            rules
            mermaid
        Hooks
            check-memory
        Base UI
            tokens.css
            components.css
```

## 4§ Class diagram — data model

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#2FBF5E', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1E9447', 'lineColor': '#0D9488', 'fontSize': '14px'}}}%%
classDiagram
    class CLAUDE_md {
        +string scope
        +Table routingTable
        +Index skillIndex
        +loadRule(format) Rule
    }
    class Rule {
        +string name
        +string description
        +string updated
        +apply()
    }
    class Skill {
        +string name
        +SKILL_md manifest
        +assets/ templates
        +invoke()
    }
    class Hook {
        +string event
        +Script handler
        +int exitCode
        +run()
    }
    CLAUDE_md "1" --> "*" Rule : loads on-demand
    CLAUDE_md "1" --> "*" Skill : loads on-demand
    CLAUDE_md "1" --> "0..*" Hook : configures
    Rule <|-- AlwaysApply
    Rule <|-- OnDemand
```

## 5§ Git graph — branching strategy

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#2FBF5E', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1E9447', 'git0': '#2FBF5E', 'git1': '#0D9488', 'git2': '#0284C7', 'gitBranchLabel0': '#fff', 'gitBranchLabel1': '#fff', 'gitBranchLabel2': '#fff'}}}%%
gitGraph
   commit id: "v0.1.0 — initial"
   branch feature/base-ui
   checkout feature/base-ui
   commit id: "add tokens.css"
   commit id: "add components.css"
   commit id: "add demo.html"
   checkout main
   merge feature/base-ui id: "merge base-ui"
   commit id: "v0.2.0 — release"
```

## 6§ Gantt — project timeline

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#2FBF5E', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1E9447', 'lineColor': '#0D9488', 'fontSize': '14px'}}}%%
gantt
    title Harness Roadmap
    dateFormat YYYY-MM-DD
    section Phase 2
    Skills             :done, p2, 2026-05-15, 21d
    section Phase 3
    Agents             :active, p3, 2026-06-01, 14d
    section Phase 4
    Docs               :done, p4, 2026-06-05, 7d
    section Phase 5
    Session learnings  :p5, after p4, 5d
```

## 7§ Kanban — task board
Requires Mermaid v11+.

```mermaid
---
config:
  kanban:
    ticketBaseUrl: ''
---
kanban
  column1["📋 Backlog"]
    task1["Add agents phase"]
    task2["Session 5 review"]
  column2["🔄 In Progress"]
    task3["Mermaid skill update"]@{ priority: 'High' }
    task4["Base UI concave"]@{ priority: 'High' }
  column3["✅ Done"]
    task5["skills"]
    task6["rules"]
    task7["html-style rule"]
    task8["base-ui v0.3"]
```

## 8§ Fishbone — root cause analysis
Requires Mermaid v11+. Keyword is `ishikawa`.

```mermaid
%%{init: {'theme': 'base'}}%%
ishikawa
  title Skill quality degradation
  accTitle: Root causes of skill quality issues
  accDescr: Fishbone diagram — why harness skills degrade over time
  section Standards
    Spec drift : External standards change without skill refresh
    No staleness rule : updated field not checked before use
  section Process
    Research step skipped : Conditional research bypassed incorrectly
    Single template : Edge cases not covered by one template
  section Context
    Long session context : Key instructions buried by prior output
    Stale examples : Templates reference removed or renamed features
```

## 9§ Pie chart — proportional data

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#2FBF5E', 'fontSize': '14px', 'pie1': '#2FBF5E', 'pie2': '#0D9488', 'pie3': '#0284C7', 'pie4': '#10b981', 'pie5': '#f59e0b'}}}%%
pie title Skill categories by count
    "Authoring" : 5
    "Documentation" : 3
    "Visualization" : 2
    "Audit" : 1
    "Utility" : 2
```

## 10§ Quadrant chart — effort vs. impact

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#2FBF5E', 'fontSize': '14px'}}}%%
quadrantChart
    title Skill effort vs. impact
    x-axis Low effort --> High effort
    y-axis Low impact --> High impact
    quadrant-1 High value — prioritize
    quadrant-2 Quick wins — do first
    quadrant-3 Fill only if needed
    quadrant-4 Reconsider
    skills: [0.35, 0.85]
    mermaid: [0.25, 0.70]
    lean-review: [0.65, 0.80]
    subagents: [0.75, 0.65]
    file-license: [0.20, 0.45]
```

## 11§ XY chart — metric time series

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'backgroundColor': '#0f172a', 'plotColorPalette': '#2FBF5E'}}}}%%
xychart-beta
    title "Token usage by skill (avg per invocation)"
    x-axis ["skills", "rules", "mermaid", "explain", "lean-review"]
    y-axis "Tokens (k)" 0 --> 80
    bar [32, 24, 18, 15, 55]
    line [32, 24, 18, 15, 55]
```

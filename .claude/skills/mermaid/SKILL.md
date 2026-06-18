---
name: mermaid
description: Generate visually rich, GitHub-renderable Mermaid diagrams. All diagram types, base-ui color system, semantic shapes, classDef, linkStyle, themeVariables, and harness use cases.
updated: 2026-06-12
---

# Mermaid

## 1§ Purpose
Produce fully styled, visually rich Mermaid diagrams for READMEs, architecture
documentation, workflow references, and skill/rule descriptions. Go beyond functional
diagrams — apply color systems, semantic shapes, and visual hierarchy so the diagram
communicates structure at a glance.

## 2§ Use when
- A README or document needs an architecture diagram and no screenshot exists.
- A workflow, lifecycle, state machine, or decision flow needs visual representation.
- Any other skill instructs "load the mermaid skill" before producing a diagram.
- User asks for a diagram, chart, or visual of any kind.

## 3§ Hard constraints
- GitHub-safe colors only: hex values (`#2FBF5E`) in `classDef` and `themeVariables`.
  Named CSS colors (`red`, `blue`) are ignored by Mermaid's renderer.
- Emoji in node labels: always wrap in double quotes — `["🔧 text"]`. Unquoted
  emoji break the parser.
- `stroke-dasharray` commas: escape as `\,` — regular commas are Mermaid delimiters.
- No gradients, no CSS injection, no external fonts — not supported on GitHub.
- Color contrast: text color must achieve WCAG AA minimum (4.5:1) against node fill.
  White text (`color:#fff`) on dark fills; dark text (`color:#0f172a`) on light fills.
- Use `%%{init: {...}}%%` at the top of the diagram block for theme and curve config.
  Mermaid v11+ also supports frontmatter config, but `%%{init}%%` has wider support.
- Kanban (`kanban`) and Fishbone (`ishikawa`) require Mermaid v11+; note version
  dependency if rendering outside GitHub.

## 4§ Diagram type selector

| Use case | Diagram type | Syntax keyword |
|---|---|---|
| Architecture, data flow, decision logic | Flowchart | `flowchart TD` / `flowchart LR` |
| API calls, tool invocations, time sequences | Sequence | `sequenceDiagram` |
| State machines, lifecycle phases | State | `stateDiagram-v2` |
| Feature overview, topic taxonomy | Mindmap | `mindmap` |
| Class / data model relationships | Class | `classDiagram` |
| Git branching strategy | Git graph | `gitGraph` |
| Project timeline, phases, milestones | Gantt | `gantt` |
| Task board, status tracking | Kanban (v11+, see 3§) | `kanban` |
| Root cause analysis | Fishbone (v11+, see 3§) | `ishikawa` |
| Proportional data | Pie chart | `pie` |
| Two-axis positioning | Quadrant | `quadrantChart` |
| Metric time series | XY chart | `xychart-beta` |

Direction for flowcharts: `TD` (top-down) for hierarchies and trees;
`LR` (left-right) for pipelines and sequential flows.

## 5§ Color system

All diagrams default to the base-ui brand palette. This aligns harness diagrams
with the visual identity defined in `base-ui/tokens.css`.

### 5.1§ Semantic classDef palette
```text
Green    — primary process nodes       fill:#2FBF5E, stroke:#1E9447, color:#fff
Teal     — secondary / alternative     fill:#0D9488, stroke:#0A7A6F, color:#fff
Blue     — entry / terminal / accent   fill:#0284C7, stroke:#0369A1, color:#fff
Emerald  — success / output / done     fill:#10b981, stroke:#047857, color:#fff
Amber    — warning / pending           fill:#f59e0b, stroke:#d97706, color:#0f172a
Red      — error / failure / blocked   fill:#ef4444, stroke:#dc2626, color:#fff
Slate    — I/O, data, peripheral       fill:#1e293b, stroke:#334155, color:#94a3b8
Ink      — storage / persistence       fill:#0f172a, stroke:#2FBF5E, color:#a5b4fc
```

### 5.2§ Standard classDef block
Include this block verbatim at the top of any flowchart. Remove unused classes
before delivery.

```mermaid
classDef entry   fill:#0284C7,stroke:#0369A1,color:#fff,font-weight:bold
classDef process fill:#2FBF5E,stroke:#1E9447,color:#fff
classDef alt     fill:#0D9488,stroke:#0A7A6F,color:#fff
classDef success fill:#10b981,stroke:#047857,color:#fff
classDef warning fill:#f59e0b,stroke:#d97706,color:#0f172a
classDef error   fill:#ef4444,stroke:#dc2626,color:#fff
classDef io      fill:#1e293b,stroke:#334155,color:#94a3b8
classDef store   fill:#0f172a,stroke:#2FBF5E,color:#a5b4fc
```

### 5.3§ themeVariables init block
Add to the top of any diagram requiring global color control:

```text
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor':       '#2FBF5E',
    'primaryTextColor':   '#ffffff',
    'primaryBorderColor': '#1E9447',
    'lineColor':          '#0D9488',
    'secondBkgColor':     '#0f172a',
    'fontSize':           '14px'
  },
  'flowchart': { 'curve': 'cardinal' }
}}%%
```

Available `curve` values: `linear`, `cardinal`, `catmullRom`, `stepBefore`,
`stepAfter`. Use `cardinal` for smooth organic curves; `linear` for strict
technical diagrams.

### 5.4§ Subgraph background
Style subgraphs with classDef on the subgraph id, or use 8-digit hex for
semi-transparency (last two digits = opacity, `80` = 50%):

```text
classDef zone fill:#2FBF5E20,stroke:#2FBF5E,color:#fff
class subgraphId zone
```

## 6§ Node shape reference

Use shapes as semantic signals — the shape itself communicates node function.

```text
Terminal / entry / exit:
  (["🚀 Start"])        stadium — rounded pill; use for BEGIN / END

Standard process:
  ["⚙️ Step"]           rectangle — default; any operation or step

Decision / branch:
  {"❓ Yes or No?"}     diamond — any condition or branch point

Event / hook / trigger:
  {{"⚡ SessionStart"}} hexagon — asynchronous event, lifecycle hook

I/O input:
  [/"📥 Input"/]        parallelogram — data entering a system

I/O output:
  [\"📤 Output"\]       inverse parallelogram — data leaving a system

Database / storage:
  [("🗄️ Store")]        cylinder — persistent storage, database, file

Reusable procedure:
  [["📦 Subroutine"]]   subroutine — referenced component, reusable block

Circle (connector):
  (("🔵"))              circle — off-page connector, event bubble

Double circle:
  ((("●")))             double circle — start/end in state machine style
```

## 7§ Styling techniques

### 7.1§ classDef application
```mermaid
classDef process fill:#2FBF5E,stroke:#1E9447,color:#fff,font-weight:bold
A["Step"]:::process
B["Step"]:::process
class C,D process
```

### 7.2§ Individual node override
Use `style` for one-off styling that should not be a class:
```mermaid
style A fill:#0284C7,stroke:#0369A1,color:#fff,stroke-width:3px
```

### 7.3§ Edge styling with linkStyle
Index is 0-based, counted in order of `-->` declarations:
```mermaid
linkStyle 0     stroke:#0D9488,stroke-width:3px
linkStyle 1,2   stroke:#2FBF5E,stroke-width:2px
linkStyle default stroke:#94a3b8,stroke-width:1.5px
```

Dashed edge:
```mermaid
linkStyle 3 stroke:#ef4444,stroke-dasharray:6\,3,stroke-width:2px
```

### 7.4§ Labeled edges with semantic color
```mermaid
A -->|"✅ success"| B
A -->|"❌ error"| C
A -.->|"optional"| D
A ==>|"critical path"| E
```

Edge types: `-->` solid, `-.->` dashed, `==>` thick, `--o` circle end,
`--x` cross end, `<-->` bidirectional.

### 7.5§ Subgraphs
```mermaid
subgraph zone["📦 Zone Label"]
    direction LR
    A["Node"]:::process
    B["Node"]:::process
end
classDef zoneStyle fill:#2FBF5E20,stroke:#2FBF5E,stroke-dasharray:4\,2
class zone zoneStyle
```

## 8§ Diagram templates

One complete, runnable template per diagram type lives in the assets — load the
matching one, adapt data and labels, remove unused sections before delivery:
- [assets/flowchart.template.md] — flowchart, annotated: all classDefs, shapes, linkStyle
- [assets/diagram-templates.md] — sequence, state machine, mindmap, class diagram,
  git graph, gantt, kanban (v11+), fishbone (v11+), pie, quadrant, XY chart

## 9§ Harness use cases
Diagrams that add specific value to the harness and its skills:

| Context | Diagram type | What to show |
|---|---|---|
| CLAUDE.md / README | Flowchart TD | Configuration loading hierarchy (session → CLAUDE.md → rules/skills/agents) |
| Skill pipeline | Flowchart LR | Skill invocation: index → SKILL.md → assets |
| Hook lifecycle | Sequence | event → script → exit code → Claude action |
| Content routing | Flowchart TD | CLAUDE.md vs rules vs settings vs hooks |
| Agent spawn | Sequence | Claude → agent → tools → result |
| Review pipeline | Flowchart LR | scope → dimensions → findings |
| Lifecycle overview | Sequence | Full session lifecycle: SessionStart → work → PostToolUse |
| Roadmap / sprint | Kanban | Current work items by status |
| Release history | Git graph | Branch and merge strategy |
| Phase timeline | Gantt | Project phases with dependencies |

## 10§ Workflow
1. Identify the diagram type from §4. If unclear, default to `flowchart TD`.
2. Draft the nodes and edges first — structure before styling.
3. Apply the `%%{init}%%` block (§5.3) if global color control is needed.
4. Apply the standard classDef block (§5.2). Remove unused classes.
5. Assign shapes semantically using §6. Match shape to node function.
6. Assign classes using `:::className` inline syntax.
7. Apply `linkStyle` for critical or semantic edges (§7.3).
8. Add `subgraph` groupings where logical zones exist (§7.5).
9. Verify: all node labels with emoji use double quotes; `stroke-dasharray`
   commas are escaped; no named colors.
10. Deliver the diagram block. State which diagram type was chosen and why.

## 11§ Output contract
Must include:
- A fenced code block with ` ```mermaid ` identifier
- `%%{init}%%` block when more than 3 color classes are used
- `classDef` for every distinct node role (never leave all nodes unstyled)
- Double-quoted labels for any node containing emoji or special characters
- At least 3 distinct node shapes when the diagram has 6+ nodes

Must not include:
- Named CSS colors in `classDef` or `themeVariables`
- Unescaped commas in `stroke-dasharray`
- Bare emoji in unquoted labels
- Diagrams with all nodes the same shape and color
- Unfilled placeholders in node text

## 12§ Associated documents
- [assets/flowchart.template.md] — annotated flowchart template with all classDefs, shapes, and linkStyle
- [assets/diagram-templates.md] — runnable templates for all other diagram types (sequence, state, mindmap, class, git graph, gantt, kanban, fishbone, pie, quadrant, XY chart)

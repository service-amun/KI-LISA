# project-new example — resulting scaffold for "Acme Dashboard"

## Input
- Project name: Acme Dashboard
- Parent: default (~/.claude/projects/)
- Desktop shortcut: yes
- Copyright holder: Jane Smith

## Created path
`C:\Users\jane\.claude\projects\acme-dashboard\`

## Directory tree
```
acme-dashboard/
├── .claude/
│   ├── projects/          # child projects go here
│   └── settings.local.json
├── CLAUDE.local.md        # pre-filled with 8 sections; not committed
├── .gitignore             # excludes CLAUDE.local.md and settings.local.json
├── LICENSE                # MIT, 2026, Jane Smith
├── README.md
├── README.de.md
├── CHANGELOG.md
└── PROJECT.md
```

## Desktop shortcut
`C:\Users\jane\Desktop\acme-dashboard.lnk` → targets `acme-dashboard/`

## CLAUDE.local.md (first 8 lines after scaffold)
```markdown
# Acme Dashboard

## 1§ Commands
- `<test-command>` — <purpose>
...
```

## Nesting example
A child project inside Acme Dashboard:
`~/.claude/projects/acme-dashboard/.claude/projects/auth-service/`
Invoke `new-project` from within `acme-dashboard/.claude/projects/` — the skill
detects the context and offers that directory as the parent.

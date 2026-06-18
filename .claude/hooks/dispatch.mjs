#!/usr/bin/env node
// Cross-platform hook dispatcher. Claude Code runs on Node, so `node` is always
// present on the host — this avoids requiring PowerShell on macOS/Linux and lets
// settings.json use one identical command line on every platform.
//
// Usage in settings.json:
//   node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs <hook-name>
//
// Picks <hook-name>.ps1 on Windows (pwsh) and <hook-name>.sh elsewhere (bash),
// forwards stdin/stdout/stderr unchanged, and propagates the child's exit code so
// exit 2 still blocks a tool call or compaction.

import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const name = process.argv[2];
if (!name) process.exit(0);

const hooksDir = dirname(fileURLToPath(import.meta.url));
const isWindows = process.platform === "win32";

const [cmd, args] = isWindows
  ? ["pwsh", ["-NonInteractive", "-File", join(hooksDir, `${name}.ps1`)]]
  : ["bash", [join(hooksDir, `${name}.sh`)]];

const child = spawn(cmd, args, { stdio: "inherit" });

// Interpreter missing (e.g. pwsh/bash not installed) → exit 0 so a missing tool
// never blocks legitimate work.
child.on("error", () => process.exit(0));

child.on("close", (code, signal) => {
  if (signal) process.exit(1);
  process.exit(code ?? 0);
});

---
name: visual-verify
description: Mandate for visual verification of UI output. Claude must use screenshot tools after producing or modifying any visual artifact; code-only review is never sufficient.
updated: 2026-06-12
---

# Visual Verification

## 1§ Scope
Applies whenever Claude produces or modifies a visual artifact: HTML files, CSS,
charts, SVG, dashboards, or any UI component. Triggers on creation and on each
subsequent edit that could affect rendered output.

## 2§ Rules
- After producing or modifying a visual artifact: verify the rendered result with
  a screenshot tool before reporting completion.
- Tool priority order: Claude Preview MCP → Chrome Extension MCP → Computer Use screenshot.
- Start with the highest-priority available tool. If it fails:
  1. Diagnose the specific cause (timeout, not connected, access denied, port conflict).
  2. Apply one targeted repair (bring pane to foreground, restart server, request access).
  3. If the repair fails: move to the next tool in the chain.
- If all tools fail: state what was tried and why each failed. Do not claim the output is correct.
- Code review never substitutes for visual verification.

## 3§ Preferred patterns
- Bring the Preview pane to the foreground before screenshotting — avoids the built-in 30 s timeout.
- Capture console errors alongside the screenshot when Preview MCP is active; surface
  any JS errors as part of the verification result.
- Chrome Extension MCP when Preview is unavailable — DOM-aware and handles authenticated pages.
- Computer Use as last resort — requires explicit access approval per session.

## 4§ Avoid
- Claiming visual correctness based on code review alone.
- Retrying the same tool in the same way after a failure without diagnosing first.
- Switching tools without attempting one targeted repair.
- Generic failure messages — name the specific error and what was tried.

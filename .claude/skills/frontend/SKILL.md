---
name: frontend
description: Generate standalone HTML using any stored UI system; falls back to base-ui (glassmorphism, no deps) when none is registered. Component API, alert patterns, document shell, accessibility.
updated: 2026-06-13
---

# Frontend

## 1§ Purpose
Produce correct, visually consistent standalone HTML by selecting the right UI system
for the current project. A project can register any number of UI systems under
`.claude/skills/frontend/assets/`. The skill detects which system is available and
applies it. When no project-specific system is registered, base-ui is the fallback.

When the output requires interactive charts, pair it with a dedicated charting
library (e.g. ECharts).

## 2§ UI system selection
On every invocation, run this selection in order:

1. Read the project's `.claude/skills/frontend/assets/` directory. Look for
   subdirectories other than `base-ui/` — each subdirectory is a registered UI system.
2. If exactly one non-base-ui system exists: use it.
3. If multiple non-base-ui systems exist: ask the user which one to apply before
   proceeding.
4. If no non-base-ui system exists: use `base-ui/` (see §5 for its component API).
5. If the user's request names a specific system (e.g. "use Tailwind variant"):
   that overrides detection.

## 3§ Registering a UI system
A UI system is a subdirectory under `assets/` with at least:

```text
assets/<system-name>/
  tokens.css       — CSS custom properties (or equivalent design tokens)
  components.css   — component styles consuming the tokens
  README.md        — component API, markup patterns, document shell
```

Claude reads `README.md` before producing any HTML for that system. All component
usage, markup conventions, and shell structure come from that file.

## 4§ Use when
- Generating any standalone HTML file: reports, dashboards, result pages, demos,
  data summaries.
- The user requests a specific UI system from the registered list.
- No design system is specified: fall back to base-ui.
- If the project supplies its own CSS outside the `assets/` registry: reference
  that file directly and skip this skill.

## 5§ base-ui reference

Asset files:

```text
assets/base-ui/
  tokens.css      — CSS custom properties: brand, semantics, glass, bevel/concave,
                    typography, spacing, motion. Includes Google Fonts @import for
                    Roboto and Roboto Mono.
  components.css  — components consuming the tokens
  demo.html       — usage showcase; open in a browser to verify the design
```

### 5.1§ Linking

```html
<link rel="stylesheet" href="base-ui/tokens.css">
<link rel="stylesheet" href="base-ui/components.css">
```

For single-file HTML output: paste the full content of `tokens.css` then
`components.css` inside one `<style>` block.

### 5.2§ Component reference

| Class | Element | Notes |
|---|---|---|
| `.card` | Any container | Glass surface |
| `.card-raised` | Any container | Deeper shadow (`--shadow-lg`) |
| `.card-concave` | Any container | Recessed/inset surface |
| `.alert` | `<div>` | Glass callout; NO colored border or bar |
| `.alert-info` / `.alert-success` / `.alert-warning` / `.alert-error` | Added to `.alert` | Colors icon and title text only |
| `.alert-icon` | `<span>` inside `.alert` | Unicode icon; colored by modifier |
| `.alert-body` | `<div>` inside `.alert` | Flex column |
| `.alert-title` | `<span>` inside `.alert-body` | Bold label; colored by modifier |
| `.alert-text` | `<span>` inside `.alert-body` | Muted body text; never colored |
| `.badge` | `<span>` | Glass pill |
| `.badge-accent` / `.badge-info` / `.badge-success` / `.badge-warning` / `.badge-error` | Added to `.badge` | Text color only |
| `.btn` | `<button>`, `<a>` | Glass button with bevel |
| `.btn-primary` | Added to `.btn` | Brand gradient fill; one per section |
| `.btn-ghost` | Added to `.btn` | Transparent; gains glass on hover |
| `.band` | `<div>` | Brand gradient accent band |
| `.stat` | `<div>` | KPI container |
| `.stat-value` / `.stat-label` / `.stat-delta` | Children of `.stat` | — |
| `.stat-delta-up` / `.stat-delta-down` / `.stat-delta-flat` | Added to `.stat-delta` | Colored pill |
| `.progress` | `<div>` | Track |
| `.progress-bar` | `<div>` | Brand gradient; override with `-success`, `-warning`, `-error` |
| `.container` | `<div>` | Max-width 72 rem, centered |
| `.grid-2` / `.grid-3` / `.grid-4` | `<div>` | Responsive CSS grid |
| `.flex-c` | `<div>` | Flex row, vertically centered |
| `.flex-w` | `<div>` | Adds `flex-wrap: wrap` |
| `.gap-2` / `.gap-4` / `.gap-6` | `<div>` | Gap utilities |
| `.divider` | `<div>` | Labelled horizontal rule |

### 5.3§ Alert markup pattern

```html
<div class="alert alert-warning">
  <span class="alert-icon">&#x26A0;</span>
  <div class="alert-body">
    <span class="alert-title">Deprecation</span>
    <span class="alert-text">Body text here — never colored.</span>
  </div>
</div>
```

Icons by state: info `&#x2139;`, success `&#x2713;`, warning `&#x26A0;`, error `&#x2715;`.

### 5.4§ Document shell

```html
<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page Title</title>
  <link rel="stylesheet" href="base-ui/tokens.css">
  <link rel="stylesheet" href="base-ui/components.css">
</head>
<body>
<div class="container">
  <!-- content -->
</div>
</body>
</html>
```

### 5.5§ Preferred patterns
- Everything glass — `.card` everywhere; never mix flat and glass surfaces.
- Semantic state via icon + title color only — never a colored surface, border, or bar.
- Accent headings: `style="color: var(--accent)"` on `h2` / `h3`.
- Tables inside `.card` for containment and padding.
- Stat values in semantic colors: `style="color: var(--success)"` on `.stat-value`.
- Inline `style` for one-off overrides; never hardcode hex — use `var(--token)`.

### 5.6§ Avoid
- Hardcoded color hex values.
- Any colored border, bar, or strip on alerts or cards.
- Mixing flat and glass surfaces.
- More than one `.band` per page.
- Nesting `.card` inside another `.card`.
- Tables without a `.card` wrapper.

## 6§ Accessibility baseline

Apply to every generated HTML file regardless of UI system:

- Structure: semantic elements — `<main>`, `<header>`, `<nav>`, `<article>`, `<section>`.
- Images: every `<img>` needs `alt`. Decorative images get `alt=""`.
- Icon-only controls: `aria-label="Descriptive action"` on any button or link with only an icon.
- Minimum contrast: never use the faintest foreground token for body copy.

## 7§ Associated documents
- [assets/base-ui/tokens.css] — CSS custom properties
- [assets/base-ui/components.css] — component styles
- [assets/base-ui/demo.html] — usage showcase

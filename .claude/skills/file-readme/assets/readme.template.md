<!-- TEMPLATE: readme.template.md
     Chapters are ordered by reader relevance (SKILL.md §5). Keep that order.
     Strip all HTML comments before delivering the final README.
     Remove optional sections not applicable to this project.
     Replace every <PLACEHOLDER> with actual content before delivery.
     Internal mechanics (load order, lifecycle, build internals) do NOT belong here —
     they go to PROJECT.md (SKILL.md §3). Contributing only when a CONTRIBUTING.md exists.
     EVERY section is collapsible with the SAME uniform inline-heading summary so the
     disclosure arrow sits in line with the text; ALL sections (and nested blocks) are
     <details open> by default. Never a block <h2> inside <summary> (SKILL.md §3).
     Never put non-code in a code environment — a prompt/instruction is a blockquote, not a
     fenced block (SKILL.md §3). Install paths (console quick start + manual) are ### subsections
     under one Installation section. Never merge element categories; sort inventory (SKILL.md §3).
     Dynamic toolkit URLs (badges, star-history) follow SKILL.md §6; substitute USER/REPO/PACKAGE. -->

<a id="readme-top"></a>

<!-- HERO: banner first — maximum visual impact, zero reading cost (SKILL.md §6). -->
![header](https://capsule-render.vercel.app/api?type=waving&color=0:<HEX1>,100:<HEX2>&height=200&section=header&text=<PROJECT_NAME>&fontSize=38&fontColor=ffffff&animation=fadeIn&fontAlignY=36&desc=<TAGLINE>&descSize=17&descAlignY=54&descColor=e0e7ff)

<div align="center">

<!-- MULTILINGUAL: keep only when other language files exist. -->
<!-- [English](README.md) | [Deutsch](README.de.md) -->

<!-- CORE BADGE ROW: meaningful indicators only, max 4 per row. -->
![Version](https://img.shields.io/github/v/release/<GITHUB_USER>/<REPO_NAME>?style=for-the-badge)
![License](https://img.shields.io/github/license/<GITHUB_USER>/<REPO_NAME>?style=for-the-badge)
![Build](https://img.shields.io/github/actions/workflow/status/<GITHUB_USER>/<REPO_NAME>/<WORKFLOW_FILE>.yml?style=for-the-badge)

<TAGLINE — one sentence: what it does and who it is for>

<!-- OPTIONAL CALL-TO-ACTION ROW: keep only links that have a destination. -->
[Report Bug](<ISSUES_URL>) · [Request Feature](<ISSUES_URL>)

</div>

<!-- HERO VISUAL: a screenshot, GIF, or ONE content-specific diagram. A Mermaid diagram must
     encode this project's real components, counts, and flow, ordered by reader relevance
     (SKILL.md §6): PRIMARY = what you get (contents and scale), SECONDARY = how it works,
     TERTIARY = how to install (one de-emphasized node). Load the mermaid skill; verify it renders. -->
```mermaid
<CONTENT_PRIMARY_MERMAID — contents as the visual focus; mechanics secondary; install tertiary>
```

<!-- INLINE LINK ROW in place of a heading-based TOC (summary headings have no auto-anchors). -->
<div align="center">

[<SECTION_1>](#<anchor-1>) · [<SECTION_2>](#<anchor-2>) · [<SECTION_3>](#<anchor-3>)

</div>

<!-- EVERY section below uses the SAME pattern: an <a id> anchor, then a <details> whose summary
     is an inline heading-style label. Primary sections open; the inventory closed. -->
<a id="<anchor-1>"></a>

<details open>
<summary><b><font size="5"><EMOJI>&nbsp; What is <PROJECT_NAME>?</font></b></summary>

<VALUE_PROPOSITION: 2–3 sentences. What is it, who is it for, why use it over alternatives.>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

</details>

<!-- WHAT YOU GET: the inventory — open by default like every section. One section per element
     CATEGORY, never merged; one row per element, sorted; one-element categories get their own table. -->
<a id="<anchor-2>"></a>

<details open>
<summary><b><font size="5"><EMOJI>&nbsp; What you get</font></b></summary>

### <CATEGORY_A>

| <COLUMN> | <ONE SHORT CLAUSE> |
|---|---|
| <ELEMENT_1> | <what it does, one clause> |
| <ELEMENT_2> | <what it does, one clause> |

### <CATEGORY_B>

| <COLUMN> | <ONE SHORT CLAUSE> |
|---|---|
| <ELEMENT_1> | <what it does, one clause> |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

</details>

<!-- INSTALLATION: ONE section, both ways to get started as ### subsections (SKILL.md §3/§5). -->
<a id="<anchor-3>"></a>

<details open>
<summary><b><font size="5"><EMOJI>&nbsp; Installation</font></b></summary>

### 🚀 Quick start — terminal

```<LANGUAGE>
<ONE_COMMAND_SET — clone/install and run>
```

### 🛠️ Manual install — no terminal

<MANUAL_STEPS — download the release, extract, copy <FILES> into <TARGET> by hand.>

<details open>
<summary>Other install options</summary>

<!-- alternative scope, partial install — open by default like every block; reader can collapse. -->

</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

</details>

<!-- OPTIONAL USAGE: keep the same collapsible pattern. -->
<a id="usage"></a>

<details open>
<summary><b><font size="5"><EMOJI>&nbsp; Usage</font></b></summary>

```<LANGUAGE>
<REALISTIC_USAGE_EXAMPLE_FROM_THE_ACTUAL_PROJECT>
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

</details>

<!-- OPTIONAL SUPPORT: only when the author provided star/funding URLs. Same pattern. -->
<!-- <a id="support"></a>

<details open>
<summary><b><font size="5">💛&nbsp; Support</font></b></summary>

[![Stars](https://img.shields.io/github/stars/<GITHUB_USER>/<REPO_NAME>?style=social)](https://github.com/<GITHUB_USER>/<REPO_NAME>)

</details> -->

<a id="license"></a>

<details open>
<summary><b><font size="5"><EMOJI>&nbsp; License</font></b></summary>

<LICENSE_NAME> — see [LICENSE](LICENSE) for details.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

</details>

![footer](https://capsule-render.vercel.app/api?type=waving&color=0:<HEX2>,100:<HEX1>&height=120&section=footer)

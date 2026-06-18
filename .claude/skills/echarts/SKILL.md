---
name: echarts
description: Generate Apache ECharts 5 charts in standalone HTML using base-ui tokens. Correct option syntax, dark/light retheme, resize handling, 8 chart-type templates. For interactive data viz.
updated: 2026-06-12
---

# ECharts

## 1§ Purpose
Produce correct, visually consistent Apache ECharts 5 charts embedded in standalone
HTML. The skill bridges base-ui (CSS tokens, glass surfaces) and ECharts (JS rendering)
so generated reports, dashboards, and data views inherit the harness brand automatically.

Primary value: ECharts option objects have notoriously complex nested paths that LLMs
get wrong — missing `type`, wrong axis shape for pie, async in `formatter`, no
`containLabel`. This skill embeds correct patterns so generated charts work on first
render.

## 2§ Use when
- AI-generated HTML output (report, dashboard, data summary) needs interactive charts.
- User asks for a chart, graph, data plot, or visualization in an HTML file.
- Another skill produces data that would be clearer as a chart than as a table.
- The `frontend` skill is active and the output needs more than `.stat` / `.progress`.

Decision gate — use base-ui components instead of ECharts when:

| Situation | Use instead |
|---|---|
| Single progress percentage | `.progress` + `.progress-bar` from base-ui |
| 1–2 KPI numbers | `.stat` + `.stat-value` from base-ui |
| Comparison of ≤ 5 items, static | `<table>` inside `.card` |
| Trend with 1 series, 5–6 points | `.progress` bars stacked in `.card` |
| Full interactive chart, ≥ 2 series, or time series | ECharts (this skill) |

## 3§ Hard constraints
These are the most common LLM failures when generating ECharts. Apply all.

- Every series object must have `type`. ECharts ignores series without a `type` silently.
- Pie and donut series must NOT have `xAxis` / `yAxis`. Cartesian axes break pie charts.
- Donut (ring): `radius` must be an array — `['40%', '70%']`. A string gives a solid pie.
- `tooltip.formatter` must be synchronous. Async functions or Promises in formatter cause
  the tooltip to display `undefined` or hang.
- `grid: { containLabel: true }` is required in almost all cartesian charts. Without it,
  long axis labels overflow outside the canvas.
- CSS custom properties cannot be passed directly to ECharts option strings. Resolve them
  first with `getComputedStyle(document.documentElement).getPropertyValue('--token')`.
- Never use named CSS colors (`red`, `blue`) in ECharts options — specify hex or rgb().
- `chart.resize()` must be called explicitly on container resize. ECharts does not
  auto-resize. Use a `ResizeObserver` on the chart container element.
- Dark/light retheme requires dispose + reinit. ECharts themes are baked at init time;
  `setOption` cannot update theme colors after the fact.
- v6 compat note: ECharts 6 moves the legend default from `top` to `bottom`. Always
  set `legend.top` or `legend.bottom` explicitly for cross-version consistency.
- `animation: false` when generating HTML for screenshot or PDF export — prevents
  partial-render capture.

## 4§ Chart type selector

| Data question | Chart type | `series.type` |
|---|---|---|
| How does a value change over time? | Line | `'line'` |
| How do categories compare? | Bar (grouped or stacked) | `'bar'` |
| What is the proportion of a whole? | Pie or donut | `'pie'` |
| How does a cumulative total grow? | Area stacked | `'line'` + `areaStyle` + `stack` |
| Is there a correlation between two variables? | Scatter | `'scatter'` |
| Where are the hot spots in a matrix? | Heatmap | `'heatmap'` |
| What is the current level of a single metric? | Gauge | `'gauge'` |
| How does one item score across multiple dimensions? | Radar | `'radar'` |

When the data question does not fit cleanly: prefer bar (most versatile cartesian) or
line (most legible for sequence data). Avoid pie for more than 6 slices.

## 5§ Integration with base-ui

### 5.1§ Document shell
The complete shell — token resolver, `buildTheme()`, `baseOption()`, the
`makeChart()` factory, `ResizeObserver` wiring, and the `data-theme`
MutationObserver retheme block — lives in [assets/echarts-shell.template.html].
Copy it as the canonical starting point; never re-derive the JavaScript by hand.

Facts the shell depends on:
- Chart containers sit inside a `.card` with explicit `height` (280 px minimum) and `padding: 0`.
- CSS tokens are resolved via `getComputedStyle(document.documentElement).getPropertyValue('--token')`.
- `makeChart()` registers the `mage` theme before each init and merges `baseOption(type)` defaults, so option templates (7§) omit `backgroundColor`, `animation`, and `grid`.
### 5.2§ Padding on chart containers
ECharts renders inside the container's content box. Set `padding: 0` on the `.card`
and let ECharts `grid` control the internal margins. Keep `border-radius` on `.card`
for visual consistency — ECharts clips to the canvas, not the CSS border-radius.

### 5.3§ Multiple charts
For dashboards with multiple charts, collect all `{ el, option, inst }` entries in
the `charts` array. The retheme observer and resize handling already loop over the
array — no additional wiring needed.

## 6§ Loading

Use one source. In order of preference:

| Scenario | Source |
|---|---|
| Online delivery (CDN) | `https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js` |
| Offline / file:// safe | Vendored: copy `echarts.min.js` to `vendor/echarts/` next to the HTML |
| Specific patch version | `https://cdn.jsdelivr.net/npm/echarts@5.6.0/dist/echarts.min.js` |
| ECharts 6 (MaGe_UI compatible) | `https://cdn.jsdelivr.net/npm/echarts@6/dist/echarts.min.js` |

Never use `@latest` in production HTML — it will silently receive breaking major versions.

## 7§ Option templates

One complete, standalone option object per chart type. Each is the value assigned to
the `option` variable in the document shell (§5.1). Do not include the `backgroundColor`,
`animation`, or `grid` defaults — `baseOption()` adds them.

### 7.1§ Line — time series / trend

```js
{
  legend: { top: 8, left: 'center' },
  xAxis: {
    type: 'category',
    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
  },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'line',
      name: 'Revenue',
      data: [820, 932, 901, 934, 1290, 1330, 1480],
      smooth: true,
      symbol: 'circle',
      symbolSize: 6
    },
    {
      type: 'line',
      name: 'Cost',
      data: [520, 630, 580, 700, 890, 920, 1020],
      smooth: true,
      symbol: 'circle',
      symbolSize: 6
    }
  ]
}
```

### 7.2§ Bar — category comparison (grouped / stacked)

```js
/* Grouped (default): remove stack property.
   Stacked: add stack: 'total' to each series. */
{
  legend: { top: 8, left: 'center' },
  xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
  yAxis: { type: 'value' },
  series: [
    { type: 'bar', name: '2024', data: [320, 480, 330, 620] },
    { type: 'bar', name: '2025', data: [420, 380, 590, 720] }
  ]
}
```

### 7.3§ Pie and donut

```js
/* Solid pie: radius is a string.
   Donut ring: radius is an array — ['inner%', 'outer%']. */
{
  legend: { orient: 'vertical', left: 'left', top: 'middle' },
  series: [{
    type: 'pie',
    name: 'Skills by category',
    radius: ['40%', '70%'],      /* remove array → solid pie */
    center: ['60%', '50%'],
    data: [
      { value: 48, name: 'Authoring' },
      { value: 32, name: 'Documentation' },
      { value: 20, name: 'Audit' }
    ],
    label: {
      formatter: '{b}: {d}%'
    },
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } }
  }]
}
```

### 7.4§ Area stacked — cumulative part-of-whole

```js
{
  legend: { top: 8, left: 'center' },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'line',
      name: 'Rules',
      stack: 'total',
      areaStyle: { opacity: 0.4 },
      smooth: true,
      data: [120, 132, 101, 134, 90, 230]
    },
    {
      type: 'line',
      name: 'Skills',
      stack: 'total',
      areaStyle: { opacity: 0.4 },
      smooth: true,
      data: [220, 182, 191, 234, 290, 330]
    }
  ]
}
```

### 7.5§ Scatter — correlation

```js
{
  xAxis: { type: 'value', name: 'Effort', nameLocation: 'end', nameGap: 20 },
  yAxis: { type: 'value', name: 'Impact', nameLocation: 'end', nameGap: 20 },
  tooltip: {
    trigger: 'item',
    formatter: function(p) {
      return p.seriesName + '<br/>Effort: ' + p.value[0] + '<br/>Impact: ' + p.value[1];
    }
  },
  series: [{
    type: 'scatter',
    name: 'Skills',
    symbolSize: 14,
    data: [[35, 85], [25, 70], [65, 80], [75, 65], [20, 45]]
  }]
}
```

### 7.6§ Heatmap — matrix

```js
{
  tooltip: { trigger: 'item' },
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
  yAxis: { type: 'category', data: ['Morning', 'Afternoon', 'Evening'] },
  visualMap: {
    min: 0, max: 100,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: 4,
    inRange: { color: ['#0f172a', '#0D9488', '#2FBF5E'] }
  },
  series: [{
    type: 'heatmap',
    data: [
      [0,0,80],[1,0,60],[2,0,95],[3,0,40],[4,0,70],
      [0,1,30],[1,1,50],[2,1,75],[3,1,90],[4,1,55],
      [0,2,20],[1,2,85],[2,2,45],[3,2,60],[4,2,80]
    ],
    label: { show: true }
  }]
}
```

### 7.7§ Gauge — single KPI

```js
{
  series: [{
    type: 'gauge',
    radius: '85%',
    startAngle: 200,
    endAngle: -20,
    min: 0,
    max: 100,
    splitNumber: 5,
    axisLine: {
      lineStyle: {
        width: 14,
        color: [[0.3, '#ef4444'], [0.7, '#f59e0b'], [1, '#2FBF5E']]
      }
    },
    axisTick: { show: false },
    splitLine: { length: 12, lineStyle: { width: 2 } },
    pointer: { length: '60%', width: 5 },
    detail: {
      formatter: '{value}%',
      fontSize: 28,
      fontWeight: 700,
      offsetCenter: [0, '70%']
    },
    data: [{ value: 78, name: 'Completion' }]
  }]
}
```

### 7.8§ Radar — multi-dimension comparison

```js
{
  legend: { top: 8, left: 'center' },
  radar: {
    indicator: [
      { name: 'Necessity', max: 100 },
      { name: 'Token efficiency', max: 100 },
      { name: 'Usability', max: 100 },
      { name: 'Quality', max: 100 },
      { name: 'Lean', max: 100 }
    ]
  },
  series: [{
    type: 'radar',
    name: 'Skill audit',
    data: [
      { value: [90, 75, 85, 95, 80], name: 'skills' },
      { value: [70, 90, 80, 88, 72], name: 'lean-review' }
    ]
  }]
}
```

## 8§ Workflow
1. Identify the data question and select the chart type from §4.
2. Verify the decision gate (§2) — confirm a chart is warranted over a base-ui component.
3. Start from `assets/echarts-shell.template.html`. Fill in the `<title>`, page heading,
   and any `.card` layout from the `frontend` skill.
4. Place a chart container `.card` with explicit `height` (minimum 280 px; 360 px is
   standard; 480 px for gauge or radar).
5. Copy the matching option template from §7. Adapt data, labels, and series names.
6. Verify hard constraints from §3: `type` present, pie has no axes, donut `radius` is
   an array, `containLabel` in grid, no async in formatter.
7. Check the `legend.top` / `legend.bottom` property is set explicitly on every
   chart that shows a legend (multi-series cartesian, pie, radar); omit the
   legend entirely for single-series scatter, heatmap, and gauge.
8. If generating for screenshot or PDF: add `animation: false` to the option object.
9. Deliver the complete standalone HTML file. State which chart type was used and why.

## 9§ Output contract
Must include:
- One `<script>` tag loading ECharts from CDN or a note about vendored fallback
- `buildTheme()` function resolving base-ui CSS tokens
- `makeChart()` factory with `echarts.registerTheme('mage', ...)` before each init
- `ResizeObserver` on the chart container
- `MutationObserver` retheme block watching `data-theme`
- `charts` array with `{ el, option, inst }` entries
- `containLabel: true` in `grid` for all cartesian charts
- Explicit `legend.top` or `legend.bottom`

Must not include:
- CSS custom property strings (e.g. `color: 'var(--accent)'`) passed directly to ECharts
- Pie or gauge series alongside `xAxis`/`yAxis`
- Async code inside `tooltip.formatter`
- `echarts@latest` in CDN URL

## 10§ Associated documents
- [assets/echarts-shell.template.html] — complete document shell combining base-ui and ECharts; copy and fill in series option

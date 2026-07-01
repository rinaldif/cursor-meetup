---
description: "Applies automatically when generating, reviewing, or refining interactive HTML analytics dashboards, tactical data visualizations, and reporting tools."
globs: ["**/*.html", "**/*.js"]
alwaysApply: false
---

# Tactical Data Visualization Blueprint & Style Guide

Build polished, self-contained single-file HTML dashboards. For decision framing and narrative, defer to the analytics-framework skill.

**Design priority:** reliability over feature count. Prefer a working simple dashboard to a fragile elaborate one.

## 1. Demo MVP vs full dashboard

### Demo MVP (default for meetups and timeboxed builds)

**Required:**
- KPI scorecards for headline metrics
- One sortable summary table with a totals row
- Data freshness footer (row count, max timestamp, incomplete-period warning if applicable)
- Dark theme with CSS custom properties

**Charts — pick one path:**
- **Preferred for reliability:** 1–2 Chart.js charts (line + horizontal ranked bar), pinned CDN below
- **Acceptable:** CSS bar rows (`width: N%` on a div) for categorical breakdowns — no Chart.js needed

**Optional (add only if straightforward):** second tab, theme toggle, stacked composition chart

### Full dashboard (when time allows)

Add theme toggle, tabs, multi-chart layouts, stacked bars with baseline-snap legend. Do not add these if they jeopardize a working MVP.

## 2. Tech stack

Self-contained HTML. CDNs in `<head>`:

- **Styling:** `<script src="https://cdn.tailwindcss.com"></script>`
- **Charting (when used):** `<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>` — always pin this version; never use unpinned `@latest`
- **Geospatial (only when needed):** D3 v7 for choropleth maps

Do not add icon libraries. Use inline SVG for UI chrome (theme toggle, etc.).

## 3. JavaScript boot order

A single script block at the end of `<body>`. **This order is mandatory** — violations silently break tabs, tables, and charts:

1. **Declare first:** `const charts = {}`, embedded data, sort state
2. **Define functions** (chart builders, theme helpers, table render)
3. **Wire DOM:** tab clicks, table header clicks, tooltips
4. **Apply theme once** without triggering chart rebuild on first load
5. **`initCharts()` once** as the final step

**Never** call chart init or `charts[id].destroy()` from theme setup during page load. Theme changes may call `chart.update()` after mutating axis/grid colors — avoid destroy/recreate unless unavoidable.

Wrap `localStorage` in try/catch (preview and `file://` contexts may block it).

**Before handing off**, mentally verify: no console errors; tabs switch panels; table has rows; canvases show data (blank 300×150 canvases = JS died early).

## 4. Visual theme & tokens

Use CSS custom properties on `<html data-theme="dark|light">`. Default dark when no saved preference.

### Shared tokens
- **Accent:** `#F7CBCF` (series, active tabs) · **Highlight:** `#FBE8E9`
- **Positive:** `#61DB9E` dark / `#2BA86F` light · **Negative:** `#FF6363` dark / `#E04545` light · **Warning:** `#FFA86E` dark / `#E8924A` light · **Info:** `#BAE3FF` dark / `#5BA8D4` light

### Dark theme
`--bg #0D0E12` · `--card #16171F` · `--border #2A2B35` · `--heading #FFFFFF` · `--body #F8F9FA` · `--muted #9CA3AF` · `--grid #2A2B35` · neutral bar `#6B7280`

### Light theme
`--bg #F5F6F8` · `--card #FFFFFF` · `--border #E2E4EA` · `--heading #0D0E12` · `--body #1A1C24` · `--muted #6B7280` · `--grid #E5E7EB` · neutral bar `#9CA3AF` · accent text on light surfaces `#C96B78`

### Theme toggle (full dashboard only)
Header sun/moon toggle via inline SVG + `currentColor`. Persist in `localStorage`. On change, update CSS vars and chart axis/grid/legend/tooltip colors via `chart.update()`.

### Contrast
No tone-on-tone text on fills (e.g. pink on pink). Badges/pills: dark text (`#0D0E12`) on accent/highlight fills.

## 5. Data, tables & footer

- Compute ratios from aggregated totals, never average pre-computed percentages
- Show numerator/denominator in tooltips for rates and efficiency metrics
- **Tables:** sortable columns (default sort = primary metric desc), totals row at bottom, `?` help icons on non-obvious columns with `position: fixed` tooltips
- **Footer:** source, row count, max timestamp, incomplete-period warning when applicable

## 6. Charts

Use brand tokens from Section 4 — never Chart.js default palettes.

| Type | Use for |
|---|---|
| Line | Continuous trends over time |
| Horizontal bar | Ranked category comparison — single neutral fill per bar |
| Stacked bar | Mutually exclusive composition over time |

- Wrap canvases in fixed-height containers; `maintainAspectRatio: false`
- Compact charts ~180–220px; stacked/multi-series ~260–320px
- Match time grain to window (weekly for multi-month ranges)
- Custom tooltip formatting; no pie charts (horizontal bars or KPI tiles instead)

### Stacked bar baseline snap (required when using stacked bars)

Only the segment on the baseline is easy to compare across stacks. On legend click, **reorder** the stack so the clicked segment snaps to the baseline (bottom vertical / left horizontal). Do not hide series on legend click. Per-segment color is appropriate here.

### Tabs (optional)

Tab strip for distinct panels. If charts sit in hidden panels, call `chart.resize()` when a tab is first shown — but wire tab handlers before `initCharts()`.

### Maps (optional)

D3 + GeoJSON choropleth only when geography matters. Include a ranked bar chart alongside.

## 7. Never do

- Prompt the user for manual data input during generation
- Unpinned Chart.js or extra CDN libraries “just in case”
- Forward-reference `const` registries (the `charts` before initialization class of bug)
- Unique color per bar when the axis already names the category
- Pie charts, raw JSON dumps, or empty table/chart placeholders
- Causal language (“caused by”, “proves”) in auto-generated copy — use directional phrasing instead

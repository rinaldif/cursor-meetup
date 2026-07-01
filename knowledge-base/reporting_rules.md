# LLMOps Cost & Usage — Analytics Reporting Rules

| | |
|---|---|
| **Document type** | Operational knowledge base |
| **Audience** | Data analysts, FinOps, dashboard builders, LLM client agents |
| **Source table** | `llm_system_interactions` (and related CSV exports under `data/raw/`) |
| **Last reviewed** | June 2026 |
| **Status** | Active — apply to all consumer-facing and executive cost reports |

---

## Purpose

Raw LLM infrastructure logs **overstate** true operational spend and **inflate** usage metrics if queried without adjustment. The logging pipeline records rack-rate costs at request time and does not yet reflect enterprise billing corrections applied at month-end.

All analysis, SQL queries, and dashboards built on this data **must** apply the three rules below before presenting spend or usage figures to stakeholders.

---

## Rule 1 — Exclude synthetic `internal_tool` traffic

### Context

The `internal_tool` channel carries automated regression tests and health pings—not real user activity. Leaving it in skews request volume, active-user counts, and adoption trends.

### Applies to

- Request volume and usage trends
- Product adoption metrics
- Unit-economics dashboards
- Any consumer-facing usage KPI

### Filter

`internal_tool` is a **channel** value (the client surface the request came from), not a `use_case` label. Always filter on `channel`:

```sql
WHERE channel != 'internal_tool'
```

### Do not apply to

Infrastructure monitoring reports that explicitly measure synthetic test coverage (rare; label clearly if used).

---

## Rule 2 — Apply enterprise contract discount on customer-support prompt

### Context

Prompt template `03bf57d7adc83026d525c8192379aa203b71e1eb` (primary customer support template) has a **40% bulk enterprise discount** on prompt and completion tokens. Raw `cost_usd` still reflects full rack pricing; billing applies the deduction retrospectively at month-end.

### Adjustment

Multiply `cost_usd` by **0.60** for rows matching this prompt ID only.

```sql
CASE
  WHEN prompt_id = '03bf57d7adc83026d525c8192379aa203b71e1eb'
  THEN cost_usd * 0.60
  ELSE cost_usd
END
```

---

## Rule 3 — Zero out SLA-credited `tool_error` failures

### Context

The API gateway logs token cost when a request times out or fails. Per SLA, interactions that fail with an upstream **`tool_error`** are **fully credited** at month-end. Raw `cost_usd` is non-zero but the true financial obligation is $0.00.

### Adjustment

```sql
CASE
  WHEN is_failure = true AND failure_type = 'tool_error'
  THEN 0.00
  ELSE <cost from Rule 2 logic>
END
```

---

## Combined adjusted cost expression

Apply **all three rules** together when computing true operational spend:

```sql
CASE
  WHEN is_failure = true AND failure_type = 'tool_error' THEN 0.00
  WHEN prompt_id = '03bf57d7adc83026d525c8192379aa203b71e1eb' THEN cost_usd * 0.60
  ELSE cost_usd
END AS adjusted_cost_usd
```

Always combine with the usage filter from Rule 1:

```sql
SELECT
  use_case,
  COUNT(*) AS requests,
  ROUND(SUM(adjusted_cost_usd), 2) AS true_spend_usd
FROM (
  SELECT
    *,
    CASE
      WHEN is_failure = true AND failure_type = 'tool_error' THEN 0.00
      WHEN prompt_id = '03bf57d7adc83026d525c8192379aa203b71e1eb' THEN cost_usd * 0.60
      ELSE cost_usd
    END AS adjusted_cost_usd
  FROM read_csv_auto('data/raw/llm_system_interactions.csv')
  WHERE channel != 'internal_tool'
) adjusted
GROUP BY use_case
ORDER BY true_spend_usd DESC;
```

---

## Quick reference

| # | Rule | Field(s) | Action |
|---|------|----------|--------|
| 1 | Synthetic traffic | `channel` | Exclude `internal_tool` from usage metrics |
| 2 | Contract discount | `prompt_id` = `03bf57d7…` | `cost_usd × 0.60` |
| 3 | SLA credit | `is_failure` + `failure_type = 'tool_error'` | Adjusted cost = `$0.00` |

---

## Reporting checklist

Before publishing any LLMOps cost or usage report, confirm:

- [ ] `internal_tool` rows excluded from consumer usage metrics
- [ ] Adjusted cost formula applied (not raw `cost_usd` alone)
- [ ] Raw vs. adjusted spend shown when presenting to FinOps or leadership
- [ ] Data freshness and row counts documented in the dashboard footer

---

## Known limitations

- Row-level `cost_usd` in the warehouse will remain at rack rates until the billing engine backfill is deployed.
- Contract credits and SLA adjustments are applied at **month-end**; mid-month dashboards may temporarily diverge from invoiced amounts.
- These rules reflect tribal knowledge as of June 2026; verify with FinOps before changing multipliers or filters.

# Data Dictionary — LLM System Ops Telemetry (Synthetic)

This document defines the schema, column semantics, and relationships for the workshop CSV files under `data/raw/`.

**Synthetic dataset notice:** All records are fictional and designed for LLMOps analytics (cost, latency, failures, tools, feedback). Token counts and costs are **estimated** and do not represent real billing data.

## Dataset overview

- **Time coverage (UTC):** 2025-02-01 → 2025-04-30
- **Core grain:** one row in `llm_system_interactions.csv` = one **interaction** (request → response)
- **Workshop tables:** interactions (detail) + users summary (pre-aggregated per user)

## Table map

```text
llm_system_users_summary (user_id)
  └── llm_system_interactions (interaction_id, session_id, user_id, prompt_id, …)
```

Join interactions to the users summary on `user_id` when you need lifetime user rollups (tokens, primary use case, dominant country).

## Global conventions

### Timestamps
- Event timestamps use ISO 8601 UTC with a `Z` suffix (e.g. `2025-03-25T11:14:35Z`).
- Derived fields in interactions: `date_utc`, `hour_of_day_utc`, `day_of_week`.

### Channel vs use case
- **`channel`** — client surface (e.g. `web_app`, `api`, `internal_tool`). Use this for the synthetic-traffic filter (`channel != 'internal_tool'`).
- **`use_case`** — product vertical (e.g. `customer_support`, `coding_assistant`). Not the same as channel.

### Cost and token accounting (synthetic)
- Token and `cost_usd` fields are **estimated** from a synthetic pricing heuristic, not a real billing system.

## `llm_system_interactions.csv`

**Grain:** 1 row = 1 interaction  
**Primary key:** `interaction_id`  
**Foreign keys:** `session_id`, `user_id`, `prompt_id` (opaque hash; no separate lookup table in this workshop bundle)

Key columns for analytics and dashboards:

| Column | Type | Description | Notes |
|---|---:|---|---|
| `interaction_id` | string | Unique interaction ID | |
| `session_id` | string | Session ID | |
| `user_id` | string | User ID | Join to users summary |
| `prompt_id` | string | Prompt configuration hash | Used for contract-discount rule |
| `timestamp_utc` | string | Event time (UTC) | ISO 8601 `Z` |
| `channel` | string | Request channel | Includes `internal_tool` for synthetic traffic |
| `use_case` | string | Product vertical | brainstorming, coding_assistant, content_writing, customer_support, data_analysis, internal_qa |
| `country_code` | string | ISO 3166-1 alpha-2 | AE, AU, BR, CA, DE, EG, FR, GB, IN, US |
| `region` | string | AMER, APAC, EMEA | |
| `total_tokens` | int | Estimated prompt + completion tokens | Synthetic |
| `cost_usd` | float | Estimated USD cost | Apply reporting rules before executive spend |
| `is_failure` | bool | Failure flag | |
| `failure_type` | string | Failure category | `tool_error`, `none`, etc. |
| `date_utc` | string | Date from `timestamp_utc` | `YYYY-MM-DD` |

Additional columns (feedback, tools, model metadata, request/response snippets, flags) are documented in the CSV header and available for ad-hoc SQL via MCP.

## `llm_system_users_summary.csv`

**Grain:** 1 row = 1 user (aggregated over interactions)  
**Primary key:** `user_id`

| Column | Type | Description | Notes |
|---|---:|---|---|
| `user_id` | string | Unique user ID | |
| `total_sessions` | int | Distinct sessions | |
| `total_requests` | int | Total interactions | |
| `total_tokens` | int | Sum of tokens | Synthetic |
| `total_cost_usd` | float | Sum of raw `cost_usd` | Not adjusted — apply rules on interactions for true spend |
| `avg_tokens_per_request` | float | Mean tokens per interaction | |
| `primary_use_case` | string | Mode use case | |
| `primary_channel` | string | Mode channel | |
| `dominant_country_code` | string | Mode country | |
| `dominant_region` | string | Mode region | |
| `overall_failure_rate` | float | Failed / total requests | |
| `high_risk_user_flag` | bool | Synthetic triage label | |

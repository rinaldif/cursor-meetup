# LLM Analytics Workshop

Local environment for the **Cursor Meetup** LLM analytics demo — DuckDB-backed SQL over synthetic CSV data, exposed via a FastMCP server.

> **Synthetic data:** The CSVs are fictional telemetry from a public Kaggle dataset (see [Data](#data) below). They do not represent real production billing or customer data.

## Data

Source: [LLM System Ops Production Telemetry and SFT](https://www.kaggle.com/datasets/tarekmasryo/llm-system-ops-production-telemetry-and-sft/) on Kaggle (synthetic LLMOps telemetry for analytics workshops).

The full Kaggle export includes multiple CSV files. **This repo keeps only two** — enough for the meetup demo:

| File in `data/raw/` | Role |
|---|---|
| `llm_system_interactions.csv` | One row per LLM interaction (cost, tokens, use case, failures, …) |
| `llm_system_users_summary.csv` | One row per user (lifetime rollups; join on `user_id` when needed) |

Business rules in `knowledge-base/reporting_rules.md` (contract discounts, SLA credits, synthetic-traffic filters) are **workshop additions** layered on top of the raw export — they are not in the Kaggle files themselves.

## Project layout

```
├── requirements.txt
├── src/meetup_mcp/server.py      # FastMCP analytical backend
├── knowledge-base/
│   ├── reporting_rules.md
│   └── data_dictionary.md
├── data/raw/
│   ├── llm_system_interactions.csv
│   └── llm_system_users_summary.csv
└── .cursor/
    ├── mcp.json
    ├── rules/
    │   ├── project-bootstrap.mdc
    │   └── dashboard-delivery.mdc
    └── skills/
        ├── analytics-framework/SKILL.md   # Decision-first analytics behavior
        └── visual-style-guide/SKILL.md    # Dashboard UI — MVP-first, pinned Chart.js
```

During the live demo, the agent builds `reports/executive_dashboard.html` from scratch.

## Resetting for a live demo

When preparing a clean starter repo before a session, **keep** everything in the project layout above (including both skills under `.cursor/skills/`). **Remove** only generated artifacts:

| Remove | Keep |
|---|---|
| `reports/` (e.g. `executive_dashboard.html`) | `.cursor/` (`mcp.json`, `rules/`, `skills/`) |
| `scripts/` (if created during a prior run) | `knowledge-base/`, `data/raw/`, `src/meetup_mcp/` |
| `.venv/` (recreate via Quick start) | `requirements.txt`, `README.md`, `.gitignore` |
| `__pycache__/`, `.DS_Store` | (auto-generated; safe to delete anytime — Python recreates `__pycache__` on import) |

## Quick start

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the MCP server (from project root)
fastmcp run src/meetup_mcp/server.py:mcp
```

Enable the server in Cursor: **Settings → MCP** (project `.cursor/mcp.json` uses paths relative to the workspace root).

## Querying data

The `query_data` tool executes read-only DuckDB SQL. Reference CSV files with paths under `data/raw/`:

```sql
SELECT use_case, COUNT(*) AS requests
FROM read_csv_auto('data/raw/llm_system_interactions.csv')
WHERE channel != 'internal_tool'
GROUP BY 1
ORDER BY 2 DESC
```

Consult the `knowledge-base/` folder (via the `read_knowledge_base` tool) for business-logic overrides and the data dictionary before building dashboards.

**Presenter check before going live:** hard-refresh the dashboard, click every tab, confirm charts render (not blank canvases).

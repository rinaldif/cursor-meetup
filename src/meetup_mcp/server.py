import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

# Import before fastmcp — the PyPI `mcp` package must not shadow our local code.
from meetup_mcp.query_guard import validate_read_only_query  # noqa: E402

import duckdb
from fastmcp import FastMCP

KNOWLEDGE_BASE_DIR = ROOT / "knowledge-base"
DATA_RAW_DIR = ROOT / "data" / "raw"

mcp = FastMCP("CursorMeetupDemo")


def _resolve_knowledge_base_dir() -> Path | None:
    if KNOWLEDGE_BASE_DIR.is_dir():
        return KNOWLEDGE_BASE_DIR.resolve()
    return None


@mcp.tool()
def read_knowledge_base() -> str:
    """
    Read all markdown files in the knowledge-base folder: business rules,
    data dictionary, metric definitions, and reporting constraints.
    """
    kb_dir = _resolve_knowledge_base_dir()
    if kb_dir is None:
        return "Knowledge base directory not found: knowledge-base/"

    md_files = sorted(kb_dir.glob("*.md"))
    if not md_files:
        return f"No markdown files found in {kb_dir}"

    sections: list[str] = []
    for path in md_files:
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            return f"Failed to read {path.name}: {exc}"
        sections.append(f"# Source: {path.name}\n\n{content}")

    header = (
        f"Knowledge base ({len(md_files)} file{'s' if len(md_files) != 1 else ''} "
        f"from {kb_dir.name}/)\n\n"
    )
    return header + "\n\n---\n\n".join(sections)


@mcp.tool()
def query_data(sql_query: str) -> str:
    """
    Execute a read-only SQL query against CSV files under data/raw/.
    Use read_csv_auto('data/raw/<file>.csv') for table sources.
    Only SELECT (and WITH ... SELECT) queries are permitted.
    """
    clean_query = sql_query.strip()
    rejection = validate_read_only_query(clean_query, ROOT, DATA_RAW_DIR)
    if rejection:
        return f"Query rejected: {rejection}"

    try:
        os.chdir(ROOT)
        result_df = duckdb.sql(clean_query).to_df()
        return result_df.to_markdown(index=False)
    except Exception as e:
        return f"SQL Execution Error: {str(e)}"

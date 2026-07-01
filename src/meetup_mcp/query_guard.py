"""Read-only SQL guardrails for the MCP query_data tool."""

from __future__ import annotations

import re
from pathlib import Path

_FORBIDDEN = re.compile(
    r"\b("
    r"INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|"
    r"COPY|EXPORT|IMPORT|ATTACH|DETACH|LOAD|INSTALL|"
    r"SET|PRAGMA|CALL|EXECUTE|REPLACE|MERGE"
    r")\b",
    re.IGNORECASE,
)

_READ_FILE = re.compile(
    r"read_(?:csv(?:_auto)?|parquet|json|text)\s*\(\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)

_COMMENT_LINE = re.compile(r"--[^\n]*")
_COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.DOTALL)


def _strip_comments(sql: str) -> str:
    sql = _COMMENT_BLOCK.sub("", sql)
    return _COMMENT_LINE.sub("", sql)


def validate_read_only_query(sql: str, project_root: Path, data_raw_dir: Path) -> str | None:
    """
    Return an error message when the query should be rejected, else None.
    Allows SELECT / WITH ... SELECT only. CSV reads must stay under data/raw/.
    """
    stripped = sql.strip().rstrip(";").strip()
    if not stripped:
        return "Empty query."

    if ";" in stripped:
        return "Multiple SQL statements are not allowed."

    normalized = _strip_comments(stripped).strip()
    if not normalized:
        return "Empty query."

    if _FORBIDDEN.search(normalized):
        return "Only read-only SELECT queries are allowed."

    upper = normalized.lstrip().upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH") or upper.startswith("EXPLAIN")):
        return "Only SELECT queries (including WITH ... SELECT) are allowed."

    data_raw_resolved = data_raw_dir.resolve()
    project_root_resolved = project_root.resolve()

    for match in _READ_FILE.finditer(normalized):
        path_str = match.group(1)
        if Path(path_str).is_absolute():
            return f"Absolute file paths are not allowed: {path_str}"

        resolved = (project_root_resolved / path_str).resolve()
        try:
            resolved.relative_to(data_raw_resolved)
        except ValueError:
            return f"File reads must use paths under data/raw/: {path_str}"

        if not resolved.exists():
            return f"Data file not found: {path_str}"

    return None

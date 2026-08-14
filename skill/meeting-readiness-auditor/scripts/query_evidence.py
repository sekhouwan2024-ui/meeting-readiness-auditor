#!/usr/bin/env python3
"""Query a prepared evidence workspace without loading all extracted content."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


def locate_database(raw: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if path.is_dir():
        path = path / "evidence.sqlite"
    if not path.exists():
        raise FileNotFoundError(f"Evidence database not found: {path}")
    return path


def row_to_result(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys() if row[key] is not None}


def build_like_clause(columns: list[str], terms: list[str], params: list[Any]) -> str:
    if not terms:
        return "1=1"
    term_clauses = []
    for term in terms:
        column_clauses = []
        for column in columns:
            column_clauses.append(f"LOWER(COALESCE({column},'')) LIKE LOWER(?)")
            params.append(f"%{term}%")
        term_clauses.append("(" + " OR ".join(column_clauses) + ")")
    return " AND ".join(term_clauses)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", help="Workspace directory or evidence.sqlite path")
    parser.add_argument("--query", action="append", default=[], help="Keyword; repeat for AND semantics")
    parser.add_argument("--type", choices=["ppt_text", "ppt_table", "ppt_chart", "xlsx_cell", "document"])
    parser.add_argument("--file-id")
    parser.add_argument("--page", type=int)
    parser.add_argument("--sheet")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--context-rows", type=int, default=1)
    args = parser.parse_args()

    database = locate_database(args.workspace)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    results: list[dict[str, Any]] = []
    terms = [term.strip() for term in args.query if term.strip()]
    limit = max(1, min(args.limit, 200))

    requested_types = [args.type] if args.type else ["ppt_text", "ppt_table", "ppt_chart", "xlsx_cell", "document"]

    if any(item.startswith("ppt_") for item in requested_types):
        params: list[Any] = []
        block_types = []
        if "ppt_text" in requested_types:
            block_types.extend(["text", "notes"])
        if "ppt_table" in requested_types:
            block_types.append("table")
        if "ppt_chart" in requested_types:
            block_types.append("chart")
        placeholders = ",".join("?" for _ in block_types)
        params.extend(block_types)
        where = [f"p.block_type IN ({placeholders})"]
        where.append(build_like_clause(["p.text_content", "p.json_payload", "p.object_name"], terms, params))
        if args.file_id:
            where.append("p.file_id=?")
            params.append(args.file_id)
        if args.page is not None:
            where.append("p.page=?")
            params.append(args.page)
        sql = f"""
            SELECT p.source_id,
                   CASE p.block_type WHEN 'table' THEN 'ppt_table' WHEN 'chart' THEN 'ppt_chart' ELSE 'ppt_text' END AS source_type,
                   p.file_id, f.file_name, p.page, p.block_type, p.object_name,
                   p.text_content AS text, p.json_payload
            FROM ppt_blocks p JOIN files f ON f.file_id=p.file_id
            WHERE {' AND '.join(where)}
            ORDER BY p.file_id, p.page, p.source_id LIMIT ?
        """
        params.append(limit)
        results.extend(row_to_result(row) for row in connection.execute(sql, params))

    if "xlsx_cell" in requested_types:
        params = []
        where = [build_like_clause(["c.value_text", "c.formula", "c.sheet_name", "c.address"], terms, params)]
        if args.file_id:
            where.append("c.file_id=?")
            params.append(args.file_id)
        if args.sheet:
            where.append("c.sheet_name=?")
            params.append(args.sheet)
        sql = f"""
            SELECT c.source_id, 'xlsx_cell' AS source_type, c.file_id, f.file_name,
                   c.sheet_name, c.address, c.row_index, c.column_index,
                   c.value_text AS text, c.numeric_value, c.formula, c.number_format
            FROM spreadsheet_cells c JOIN files f ON f.file_id=c.file_id
            WHERE {' AND '.join(where)}
            ORDER BY c.file_id, c.sheet_name, c.row_index, c.column_index LIMIT ?
        """
        params.append(limit)
        cell_matches = [row_to_result(row) for row in connection.execute(sql, params)]
        results.extend(cell_matches)
        if args.context_rows > 0 and cell_matches:
            seen = {item["source_id"] for item in cell_matches}
            for item in cell_matches[: min(20, len(cell_matches))]:
                context_params = [item["file_id"], item["sheet_name"], item["row_index"] - args.context_rows, item["row_index"] + args.context_rows]
                context_sql = """
                    SELECT c.source_id, 'xlsx_cell' AS source_type, c.file_id, f.file_name,
                           c.sheet_name, c.address, c.row_index, c.column_index,
                           c.value_text AS text, c.numeric_value, c.formula, c.number_format
                    FROM spreadsheet_cells c JOIN files f ON f.file_id=c.file_id
                    WHERE c.file_id=? AND c.sheet_name=? AND c.row_index BETWEEN ? AND ?
                    ORDER BY c.row_index, c.column_index
                """
                for row in connection.execute(context_sql, context_params):
                    result = row_to_result(row)
                    if result["source_id"] not in seen:
                        result["context_for"] = item["source_id"]
                        results.append(result)
                        seen.add(result["source_id"])

    if "document" in requested_types:
        params = []
        where = [build_like_clause(["d.text_content", "d.json_payload", "d.page_or_section"], terms, params)]
        if args.file_id:
            where.append("d.file_id=?")
            params.append(args.file_id)
        sql = f"""
            SELECT d.source_id, 'document' AS source_type, d.file_id, f.file_name,
                   d.page_or_section, d.block_type, d.text_content AS text, d.json_payload
            FROM document_blocks d JOIN files f ON f.file_id=d.file_id
            WHERE {' AND '.join(where)}
            ORDER BY d.file_id, d.source_id LIMIT ?
        """
        params.append(limit)
        results.extend(row_to_result(row) for row in connection.execute(sql, params))

    connection.close()
    deduplicated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for result in results:
        source_id = str(result.get("source_id"))
        if source_id in seen_ids:
            continue
        seen_ids.add(source_id)
        deduplicated.append(result)
    output_limit = min(200, max(limit, limit * 3))
    output_results = deduplicated[:output_limit]
    print(json.dumps({"schema_version": "2.0", "match_count": len(deduplicated), "returned_count": len(output_results), "results": output_results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

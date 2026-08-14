#!/usr/bin/env python3
"""Validate the prepared evidence workspace and its stable schema."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

EXPECTED_VERSION = "2.0"
REQUIRED_TABLES = {"metadata", "files", "ppt_blocks", "spreadsheet_cells", "document_blocks"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    required_files = ["workspace_manifest.json", "inventory.json", "analysis_packet.json", "evidence.sqlite"]
    for name in required_files:
        if not (workspace / name).exists():
            errors.append(f"missing {name}")
    if errors:
        print(json.dumps({"valid": False, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
        return 2

    inventory = json.loads((workspace / "inventory.json").read_text(encoding="utf-8"))
    packet = json.loads((workspace / "analysis_packet.json").read_text(encoding="utf-8"))
    manifest = json.loads((workspace / "workspace_manifest.json").read_text(encoding="utf-8"))
    for label, value in [("inventory", inventory), ("analysis_packet", packet), ("manifest", manifest)]:
        if value.get("schema_version") != EXPECTED_VERSION:
            errors.append(f"{label}: schema_version must be {EXPECTED_VERSION}")
        if not value.get("workspace_id"):
            errors.append(f"{label}: missing workspace_id")
    workspace_ids = {inventory.get("workspace_id"), packet.get("workspace_id"), manifest.get("workspace_id")}
    if len(workspace_ids) != 1:
        errors.append("workspace_id mismatch across files")
    if not isinstance(inventory.get("files"), list):
        errors.append("inventory.files must be a list")
    if not isinstance(packet.get("file_summaries"), list):
        errors.append("analysis_packet.file_summaries must be a list")

    connection = sqlite3.connect(workspace / "evidence.sqlite")
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    missing_tables = REQUIRED_TABLES - tables
    if missing_tables:
        errors.append("missing database tables: " + ", ".join(sorted(missing_tables)))
    else:
        version_row = connection.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
        if not version_row or version_row[0] != EXPECTED_VERSION:
            errors.append("database schema_version mismatch")
        ok_files = connection.execute("SELECT COUNT(*) FROM files WHERE extraction_status='ok'").fetchone()[0]
        if ok_files == 0:
            errors.append("no successfully extracted files")
        failed_files = connection.execute("SELECT file_name, warning FROM files WHERE extraction_status!='ok'").fetchall()
        for file_name, warning in failed_files:
            warnings.append(f"{file_name}: {warning}")
    connection.close()

    packet_size = (workspace / "analysis_packet.json").stat().st_size
    if packet_size > 250000:
        warnings.append(f"analysis_packet.json is large ({packet_size} bytes); consider lowering packet budget")
    print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings, "packet_bytes": packet_size}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate an audit_result.json before rendering.

Strict about confirmed errors, evidence-constrained answers, and meeting simulation
rounds. Catches missing fields, unsupported certainty, duplicate issues, arithmetic
mistakes, and simulation states that do not match the available evidence.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path
from typing import Any

ALLOWED_FINDING_TYPES = {
    "confirmed_error",
    "definition_risk",
    "logic_gap",
    "visual_risk",
    "important_omission",
    "needs_investigation",
}
ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}
ALLOWED_CONFIDENCE = {"confirmed", "likely", "uncertain"}
ALLOWED_ANSWER_STATUS = {"ready", "partial", "not_ready", "decision_needed"}
ALLOWED_MEETING_STATUS = {"needs_fix", "needs_data", "ready_for_rehearsal", "ready_with_caveats"}


class SafeMath(ast.NodeVisitor):
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Name,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd,
        ast.Load,
        ast.FloorDiv,
    )

    def visit(self, node):
        if not isinstance(node, self.allowed):
            raise ValueError(f"Unsupported expression element: {type(node).__name__}")
        return super().visit(node)


def eval_expr(expr: str, variables: dict[str, Any]) -> float:
    tree = ast.parse(expr, mode="eval")
    SafeMath().visit(tree)
    values = {k: float(v) for k, v in variables.items()}
    return float(eval(compile(tree, "<formula>", "eval"), {"__builtins__": {}}, values))


def require(obj: dict, fields: list[str], where: str, errors: list[str]):
    for field in fields:
        if field not in obj or obj[field] in (None, "", []):
            errors.append(f"{where}: missing {field}")


def validate_evidence(evidence: Any, where: str, errors: list[str]):
    if not isinstance(evidence, list):
        errors.append(f"{where}: evidence must be a list")
        return
    for index, item in enumerate(evidence, start=1):
        if not isinstance(item, dict):
            errors.append(f"{where}[{index}]: evidence item must be an object")
            continue
        require(item, ["file", "page_or_sheet", "value_or_quote"], f"{where}[{index}]", errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_json")
    parser.add_argument("--write-normalized", help="Optional normalized JSON output")
    args = parser.parse_args()

    path = Path(args.audit_json)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    require(
        data,
        ["report_title", "meeting_context", "summary", "findings", "questions", "simulation", "data_requests"],
        "root",
        errors,
    )
    summary = data.get("summary", {})
    require(summary, ["meeting_status", "executive_summary"], "summary", errors)
    if summary.get("meeting_status") not in ALLOWED_MEETING_STATUS:
        errors.append(f"summary: invalid meeting_status {summary.get('meeting_status')}")
    if "readiness_score" in summary:
        warnings.append("summary.readiness_score is deprecated; use explicit issue and readiness counts")

    ids: set[str] = set()
    for index, finding in enumerate(data.get("findings", []), start=1):
        where = f"finding[{index}]"
        require(
            finding,
            [
                "id",
                "title",
                "type",
                "severity",
                "confidence",
                "location",
                "statement",
                "assessment",
                "evidence",
                "recommended_fix",
            ],
            where,
            errors,
        )
        if finding.get("id") in ids:
            errors.append(f"{where}: duplicate id {finding.get('id')}")
        ids.add(str(finding.get("id")))
        if finding.get("type") not in ALLOWED_FINDING_TYPES:
            errors.append(f"{where}: invalid type {finding.get('type')}")
        if finding.get("severity") not in ALLOWED_SEVERITIES:
            errors.append(f"{where}: invalid severity {finding.get('severity')}")
        if finding.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"{where}: invalid confidence {finding.get('confidence')}")
        if finding.get("type") == "confirmed_error" and finding.get("confidence") != "confirmed":
            errors.append(f"{where}: confirmed_error must have confidence=confirmed")
        if finding.get("type") == "confirmed_error" and len(finding.get("evidence", [])) < 1:
            errors.append(f"{where}: confirmed error requires evidence")
        validate_evidence(finding.get("evidence", []), f"{where}.evidence", errors)
        calculation = finding.get("calculation")
        if calculation:
            require(
                calculation,
                ["expression", "variables", "reported_result", "computed_result"],
                f"{where}.calculation",
                errors,
            )
            try:
                computed = eval_expr(calculation["expression"], calculation["variables"])
                claimed = float(calculation["computed_result"])
                if not math.isclose(computed, claimed, rel_tol=1e-6, abs_tol=1e-6):
                    errors.append(f"{where}: computed_result {claimed} != recalculation {computed}")
            except Exception as exc:
                errors.append(f"{where}: invalid calculation: {exc}")
        wording = (str(finding.get("assessment", "")) + " " + str(finding.get("title", ""))).lower()
        if any(term in wording for term in ["造假", "欺骗", "故意隐瞒", "fraud", "fabricat"]):
            warnings.append(f"{where}: accusatory wording requires direct evidence; use neutral wording")

    question_ids: set[str] = set()
    for index, question in enumerate(data.get("questions", []), start=1):
        where = f"question[{index}]"
        require(
            question,
            ["id", "question", "priority", "why_it_may_be_asked", "direct_answer", "next_question"],
            where,
            errors,
        )
        if question.get("id") in question_ids:
            errors.append(f"{where}: duplicate id {question.get('id')}")
        question_ids.add(str(question.get("id")))
        if question.get("priority") not in ALLOWED_SEVERITIES:
            errors.append(f"{where}: invalid priority {question.get('priority')}")
        if question.get("based_on_unfixed_error") is True:
            errors.append(f"{where}: questions must be generated after errors are fixed")
        if "evidence" not in question or "unknowns" not in question:
            errors.append(f"{where}: evidence and unknowns fields must be present")
        if not isinstance(question.get("unknowns", []), list):
            errors.append(f"{where}.unknowns: must be a list")
        validate_evidence(question.get("evidence", []), f"{where}.evidence", errors)
        if not question.get("evidence") and not question.get("unknowns"):
            errors.append(f"{where}: answer needs evidence or explicit unknowns")

    simulation = data.get("simulation", {})
    if simulation:
        require(simulation, ["title", "opening", "rounds", "summary"], "simulation", errors)
        rounds = simulation.get("rounds", [])
        if not 4 <= len(rounds) <= 8:
            errors.append("simulation.rounds: must contain 4 to 8 rounds")
        round_ids: set[str] = set()
        status_counts = {status: 0 for status in ALLOWED_ANSWER_STATUS}
        for index, round_item in enumerate(rounds, start=1):
            where = f"simulation.round[{index}]"
            require(
                round_item,
                [
                    "id",
                    "role",
                    "question",
                    "intent",
                    "answer_status",
                    "suggested_answer",
                    "prep_action",
                    "follow_up_question",
                    "avoid_answer",
                ],
                where,
                errors,
            )
            if round_item.get("id") in round_ids:
                errors.append(f"{where}: duplicate id {round_item.get('id')}")
            round_ids.add(str(round_item.get("id")))
            status = round_item.get("answer_status")
            if status not in ALLOWED_ANSWER_STATUS:
                errors.append(f"{where}: invalid answer_status {status}")
            else:
                status_counts[status] += 1
            if "evidence" not in round_item or "unknowns" not in round_item:
                errors.append(f"{where}: evidence and unknowns fields must be present")
            if not isinstance(round_item.get("unknowns", []), list):
                errors.append(f"{where}.unknowns: must be a list")
            validate_evidence(round_item.get("evidence", []), f"{where}.evidence", errors)
            if status == "ready" and not round_item.get("evidence"):
                errors.append(f"{where}: ready answer requires evidence")
            if status in {"partial", "not_ready"} and not round_item.get("unknowns"):
                errors.append(f"{where}: {status} answer requires explicit unknowns")
            if status == "not_ready" and not round_item.get("prep_action"):
                errors.append(f"{where}: not_ready answer requires a prep_action")
            if status == "decision_needed" and not round_item.get("prep_action"):
                errors.append(f"{where}: decision_needed answer requires a decision action")
            if round_item.get("question") == round_item.get("follow_up_question"):
                errors.append(f"{where}: follow_up_question must deepen the discussion")
            if len(str(round_item.get("suggested_answer", ""))) > 520:
                warnings.append(f"{where}: suggested_answer may be too long for a 20-45 second spoken answer")

        summary = simulation.get("summary", {})
        require(summary, ["total_rounds", "ready", "partial", "not_ready", "decision_needed"], "simulation.summary", errors)
        if summary:
            if int(summary.get("total_rounds", -1)) != len(rounds):
                errors.append("simulation.summary.total_rounds does not match rounds length")
            for status, count in status_counts.items():
                if int(summary.get(status, -1)) != count:
                    errors.append(f"simulation.summary.{status} does not match round count")

    for index, request in enumerate(data.get("data_requests", []), start=1):
        require(request, ["item", "reason", "priority", "owner", "deadline"], f"data_request[{index}]", errors)

    normalized = data
    normalized["validation"] = {"errors": errors, "warnings": warnings}
    if args.write_normalized:
        Path(args.write_normalized).write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

import difflib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_suggestor import get_ai_review
from code_parser import parse_code
from code_visitor import track_variable_context
from error_detector import report_unused


def _static_issue_strings(issues: dict) -> list:
    output = []
    for item in issues.get("unused_imports", []):
        output.append(f"Unused import: {item.get('name', 'unknown')}")
    for item in issues.get("unused_variables", []):
        output.append(f"Unused variable: {item.get('name', 'unknown')}")
    for item in issues.get("unused_functions", []):
        output.append(f"Unused function: {item.get('name', 'unknown')}")
    return output


def _merge_issue_lists(static_issues: list, ai_issues: list) -> list:
    merged = []
    seen = set()
    for item in static_issues + ai_issues:
        text = str(item).strip()
        if not text:
            continue
        key = text.lower()
        if key not in seen:
            seen.add(key)
            merged.append(text)
    return merged


def _normalize_improved_code(value, original_code: str) -> str:
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return original_code
        if (
            cleaned.startswith("{")
            and cleaned.endswith("}")
            and ('"import ' in cleaned or "'import " in cleaned)
        ):
            return original_code
        return value

    if isinstance(value, (list, tuple)):
        if value and all(isinstance(item, str) for item in value):
            joined = "\n".join(value).strip()
            return joined if joined else original_code
        return original_code

    if isinstance(value, dict):
        for key in ("improved_code", "code", "refactored_code"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate
        return original_code

    return original_code


def analyze_code_pipeline(code_string: str, language: str = "Python") -> dict:
    parse_result = parse_code(code_string)
    if not parse_result.get("success", False):
        error_obj = parse_result.get("error", {})
        message = error_obj.get("message", "Syntax error")
        return {"error": message, "success": False}

    issues = report_unused(code_string)
    variable_context = track_variable_context(code_string)
    ai_review = get_ai_review(code_string, issues, language)
    if not isinstance(ai_review, dict):
        ai_review = {
            "quality_grade": "N/A",
            "analysis_summary": "Parse error",
            "issues_found": [],
            "improved_code": code_string,
            "detailed_explanations": {},
            "ai_fallback": True,
        }

    improved_code = _normalize_improved_code(
        ai_review.get("improved_code", code_string), code_string
    )

    static_issues = _static_issue_strings(issues)
    ai_issues = ai_review.get("issues_found", [])
    if not isinstance(ai_issues, list):
        ai_issues = [str(ai_issues)]
    merged_issues = _merge_issue_lists(static_issues, ai_issues)

    original_lines = code_string.splitlines()
    improved_lines = improved_code.splitlines()

    raw_diff = list(
        difflib.unified_diff(
            original_lines,
            improved_lines,
            fromfile="original",
            tofile="improved",
            lineterm="",
        )
    )

    diff_lines = []
    for idx, line in enumerate(raw_diff, start=1):
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            line_type = "add"
        elif line.startswith("-"):
            line_type = "remove"
        else:
            line_type = "equal"
        diff_lines.append({"type": line_type, "line": line, "num": idx})

    return {
        "success": True,
        "quality_grade": ai_review.get("quality_grade", "N/A"),
        "issues_count": len(merged_issues),
        "analysis_summary": ai_review.get("analysis_summary", ""),
        "original_code": code_string,
        "improved_code": improved_code,
        "issues_found": merged_issues,
        "detailed_explanations": ai_review.get("detailed_explanations", {}),
        "ai_fallback": bool(ai_review.get("ai_fallback", False)),
        "static_analysis": issues,
        "variable_context": variable_context,
        "diff_lines": diff_lines,
    }

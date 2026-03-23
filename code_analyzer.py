import difflib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_suggestor import get_ai_review
from code_parser import parse_code
from error_detector import report_unused


def analyze_code_pipeline(code_string: str, language: str = "Python") -> dict:
    parse_result = parse_code(code_string)
    if not parse_result.get("success", False):
        error_obj = parse_result.get("error", {})
        message = error_obj.get("message", "Syntax error")
        return {"error": message, "success": False}

    issues = report_unused(code_string)
    ai_review = get_ai_review(code_string, issues, language)
    if not isinstance(ai_review, dict):
        ai_review = {
            "quality_grade": "N/A",
            "analysis_summary": "Parse error",
            "issues_found": [],
            "improved_code": code_string,
            "detailed_explanations": {},
        }

    improved_code = ai_review.get("improved_code", code_string)
    if not isinstance(improved_code, str):
        improved_code = str(improved_code)

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
        "issues_count": len(ai_review.get("issues_found", [])),
        "analysis_summary": ai_review.get("analysis_summary", ""),
        "original_code": code_string,
        "improved_code": improved_code,
        "issues_found": ai_review.get("issues_found", []),
        "detailed_explanations": ai_review.get("detailed_explanations", {}),
        "static_analysis": issues,
        "diff_lines": diff_lines,
    }

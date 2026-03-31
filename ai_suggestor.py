import ast
import difflib
import json
import os
import re
import sys

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def _build_model() -> ChatGroq:
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )


def _static_issue_strings(issues: dict) -> list:
    output = []
    for imp in issues.get("unused_imports", []):
        output.append(f"Unused import: {imp.get('name', 'unknown')}")
    for fn in issues.get("unused_functions", []):
        output.append(f"Unused function: {fn.get('name', 'unknown')}")
    for var in issues.get("unused_variables", []):
        output.append(f"Unused variable: {var.get('name', 'unknown')}")
    return output


def _grade_from_issue_count(issue_count: int) -> str:
    if issue_count <= 2:
        return "A"
    if issue_count <= 5:
        return "B"
    if issue_count <= 10:
        return "C"
    return "D"


def _issues_text(issues: dict, include_lines: bool = False) -> str:
    lines = []
    for imp in issues.get("unused_imports", []):
        if include_lines:
            lines.append(f"- Unused import: {imp.get('name', 'unknown')} at line {imp.get('line', '?')}")
        else:
            lines.append(f"- Remove unused import: {imp.get('name', 'unknown')}")
    for fn in issues.get("unused_functions", []):
        if include_lines:
            lines.append(f"- Unused function: {fn.get('name', 'unknown')} at line {fn.get('line', '?')}")
        else:
            lines.append(f"- Remove unused function: {fn.get('name', 'unknown')}")
    for var in issues.get("unused_variables", []):
        if include_lines:
            lines.append(f"- Unused variable: {var.get('name', 'unknown')} at line {var.get('line', '?')}")
        else:
            lines.append(f"- Remove unused variable: {var.get('name', 'unknown')}")
    return "\n".join(lines)


def _extract_json_text(raw_text: str) -> str:
    text = raw_text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            section = part.strip()
            if section.startswith("json"):
                section = section[4:].strip()
            if section.startswith("{"):
                text = section
                break

    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    return text


def _parse_json_dict(raw: str) -> dict:
    parsed = json.loads(_extract_json_text(raw))
    if not isinstance(parsed, dict):
        raise ValueError("Response is not a JSON object")
    return parsed


def _strip_code_fences(raw_code: str) -> str:
    cleaned = raw_code.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _looks_like_non_code_payload(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    if t.startswith("{") and t.endswith("}"):
        return True
    if re.search(r"\bquality_grade\b|\banalysis_summary\b|\bissues_found\b", t):
        return True
    return False


def _count_defs(source: str) -> int:
    try:
        tree = ast.parse(source)
    except Exception:
        return 0
    return sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in ast.walk(tree))


def _is_overexpanded_rewrite(original_code: str, candidate_code: str) -> bool:
    original = original_code.strip()
    candidate = candidate_code.strip()
    if not original or not candidate:
        return False

    orig_lines = len(original.splitlines())
    cand_lines = len(candidate.splitlines())

    # Tiny inputs should not explode into large unrelated templates.
    if orig_lines <= 3 and cand_lines > 12:
        return True

    # For any input, reject extreme growth in rewritten output.
    if cand_lines > max(30, orig_lines * 6):
        return True

    similarity = difflib.SequenceMatcher(None, original, candidate).ratio()
    if orig_lines <= 8 and cand_lines > (orig_lines * 3) and similarity < 0.2:
        return True

    original_defs = _count_defs(original)
    candidate_defs = _count_defs(candidate)
    if original_defs == 0 and candidate_defs >= 3 and cand_lines > (orig_lines * 2):
        return True

    return False


def get_review_metadata(code_string: str, issues: dict, language: str) -> dict:
    llm = _build_model()
    issues_text = _issues_text(issues, include_lines=True)

    prompt = f"""You are a senior {language} code reviewer. Analyze this {language} code and the issues found.

CODE:
{code_string}

STATIC ANALYSIS ISSUES:
{issues_text if issues_text else "None found"}

Respond with ONLY a JSON object. No markdown. No code fences. No text outside the JSON.
The JSON must have exactly these keys:

{{
  "quality_grade": "single letter A B C D or F",
  "analysis_summary": "2 sentence summary of what is wrong",
  "issues_found": ["issue 1", "issue 2", "issue 3"],
  "scalability_impact": "2 sentences about scalability",
  "time_space_complexity": "describe original vs improved complexity",
  "security_vulnerabilities": "any security issues found or None",
  "best_practices": "list best practices violations found"
}}

IMPORTANT: issues_found must be a JSON array of strings.
Do NOT include any code in your response."""

    messages = [
        SystemMessage(content="You are a strict code reviewer. Respond only with valid JSON."),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip() if hasattr(response, "content") else str(response).strip()

    try:
        parsed = _parse_json_dict(raw)
        issues_found = parsed.get("issues_found", [])
        if not isinstance(issues_found, list):
            issues_found = [str(issues_found)]
        return {
            "quality_grade": str(parsed.get("quality_grade", "N/A")),
            "analysis_summary": str(parsed.get("analysis_summary", "")),
            "issues_found": [str(x) for x in issues_found],
            "scalability_impact": str(parsed.get("scalability_impact", "")),
            "time_space_complexity": str(parsed.get("time_space_complexity", "")),
            "security_vulnerabilities": str(parsed.get("security_vulnerabilities", "")),
            "best_practices": str(parsed.get("best_practices", "")),
        }
    except Exception:
        return {
            "quality_grade": "N/A",
            "analysis_summary": "Could not parse AI metadata response.",
            "issues_found": [],
            "scalability_impact": "",
            "time_space_complexity": "",
            "security_vulnerabilities": "",
            "best_practices": "",
        }


def get_improved_code(code_string: str, issues: dict, language: str) -> str:
    llm = _build_model()
    issues_text = _issues_text(issues, include_lines=False)

    prompt = f"""You are an expert {language} developer. Rewrite the following code applying ALL improvements listed.

ORIGINAL CODE:
{code_string}

REQUIRED IMPROVEMENTS:
{issues_text if issues_text else "- Improve readability and keep behavior equivalent"}
- Keep behavior equivalent while improving clarity and maintainability
- Apply language-idiomatic patterns and modern best practices
- Preserve public interfaces unless they are clearly incorrect

OUTPUT RULES:
- Output ONLY raw {language} code
- Do NOT include explanation
- Do NOT include markdown
- Do NOT include triple backticks
- Start directly with source code
- Output must be valid {language}
"""

    messages = [
        SystemMessage(content=f"You are a {language} expert. Output only raw {language} code with no explanation and no markdown."),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip() if hasattr(response, "content") else str(response).strip()
    code = _strip_code_fences(raw)

    if _looks_like_non_code_payload(code):
        return code_string
    if _is_overexpanded_rewrite(code_string, code):
        return code_string
    return code


def get_ai_review(code_string: str, issues: dict, language: str = "Python") -> dict:
    try:
        metadata = get_review_metadata(code_string, issues, language)
        improved = get_improved_code(code_string, issues, language)

        fallback = not improved.strip() or improved.strip() == code_string.strip()
        if fallback:
            fallback_issues = _static_issue_strings(issues)
            fallback_grade = _grade_from_issue_count(len(fallback_issues))
            return {
                "quality_grade": fallback_grade,
                "analysis_summary": "AI rewrite was empty or unchanged, so static analysis findings are shown.",
                "issues_found": fallback_issues,
                "improved_code": code_string,
                "detailed_explanations": {
                    "scalability_impact": metadata.get("scalability_impact", ""),
                    "time_space_complexity": metadata.get("time_space_complexity", ""),
                    "security_vulnerabilities": metadata.get("security_vulnerabilities", ""),
                    "best_practices": metadata.get("best_practices", ""),
                },
                "ai_fallback": True,
            }

        return {
            "quality_grade": metadata.get("quality_grade", "N/A"),
            "analysis_summary": metadata.get("analysis_summary", ""),
            "issues_found": metadata.get("issues_found", []),
            "improved_code": improved,
            "detailed_explanations": {
                "scalability_impact": metadata.get("scalability_impact", ""),
                "time_space_complexity": metadata.get("time_space_complexity", ""),
                "security_vulnerabilities": metadata.get("security_vulnerabilities", ""),
                "best_practices": metadata.get("best_practices", ""),
            },
            "ai_fallback": False,
        }
    except Exception:
        fallback_issues = _static_issue_strings(issues)
        fallback_grade = _grade_from_issue_count(len(fallback_issues))
        return {
            "quality_grade": fallback_grade,
            "analysis_summary": "AI response format was invalid, so static analysis findings are shown.",
            "issues_found": fallback_issues,
            "improved_code": code_string,
            "detailed_explanations": {
                "scalability_impact": "Fallback mode: based on static analysis only.",
                "time_space_complexity": "Not evaluated in fallback mode.",
                "security_vulnerabilities": "Not fully evaluated in fallback mode.",
                "best_practices": "Review static findings and run regenerate for a full AI rewrite.",
            },
            "ai_fallback": True,
        }


def ask_ai_assistant(question: str, code_context: str, chat_history: list) -> str:
    model = _build_model()
    messages = [
        SystemMessage(
            content=(
                "You are an expert code reviewer. The user is asking about their code.\n"
                f"Code context:\n{code_context}"
            )
        )
    ]

    for item in chat_history:
        role = item.get("role", "").lower()
        content = item.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=question))

    try:
        response = model.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as exc:
        return f"Unable to get AI response: {exc}"

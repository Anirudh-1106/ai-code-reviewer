import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass

from language_config import LANGUAGE_EXTENSIONS, normalize_language


@dataclass
class LintResult:
    tool: str
    available: bool
    violations: list[dict]
    note: str = ""


def _run_command(cmd: list[str], timeout: int = 20) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout)
    except Exception:
        return None


def _build_violation(tool: str, message: str, line: int | None = None, column: int | None = None, code: str = "LINT") -> dict:
    return {
        "tool": tool,
        "code": code,
        "message": message,
        "line": line if line else "?",
        "column": column if column else "?",
    }


def _write_temp_source(code_string: str, language: str) -> tuple[str, str]:
    suffix = LANGUAGE_EXTENSIONS.get(language, ".txt")
    temp_dir = tempfile.mkdtemp(prefix="review_lint_")
    file_path = os.path.join(temp_dir, f"snippet{suffix}")
    with open(file_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(code_string)
    return temp_dir, file_path


def _cleanup_temp_dir(temp_dir: str) -> None:
    try:
        shutil.rmtree(temp_dir)
    except OSError:
        pass


def _parse_colon_diagnostics(tool: str, output: str, code: str = "LINT") -> list[dict]:
    issues = []
    pattern = re.compile(r"^.*?:(\d+):(\d+):\s*(.*)$")
    fallback = re.compile(r"^.*?:(\d+):\s*(.*)$")

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = pattern.match(line)
        if match:
            ln, col, msg = match.groups()
            issues.append(_build_violation(tool, msg.strip(), int(ln), int(col), code=code))
            continue
        match = fallback.match(line)
        if match:
            ln, msg = match.groups()
            issues.append(_build_violation(tool, msg.strip(), int(ln), None, code=code))
    return issues


def _lint_javascript_typescript(file_path: str, language: str) -> list[LintResult]:
    results = []

    eslint_path = shutil.which("eslint")
    if eslint_path:
        proc = _run_command([eslint_path, "--no-config-lookup", "--format", "json", file_path])
        violations = []
        if proc is not None:
            payload = (proc.stdout or "").strip()
            if payload:
                try:
                    parsed = json.loads(payload)
                    if isinstance(parsed, list):
                        for entry in parsed:
                            for msg in entry.get("messages", []):
                                violations.append(
                                    _build_violation(
                                        "eslint",
                                        msg.get("message", "Lint issue"),
                                        msg.get("line"),
                                        msg.get("column"),
                                        code=msg.get("ruleId") or "ESLINT",
                                    )
                                )
                except Exception:
                    violations.extend(_parse_colon_diagnostics("eslint", proc.stderr or proc.stdout, code="ESLINT"))
        results.append(LintResult(tool="eslint", available=True, violations=violations))
    else:
        results.append(LintResult(tool="eslint", available=False, violations=[], note="eslint not found in PATH"))

    if language == "TypeScript":
        tsc_path = shutil.which("tsc")
        if tsc_path:
            proc = _run_command([tsc_path, "--noEmit", "--pretty", "false", file_path])
            combined = f"{proc.stdout or ''}\n{proc.stderr or ''}" if proc is not None else ""
            violations = _parse_colon_diagnostics("tsc", combined, code="TSC")
            results.append(LintResult(tool="tsc", available=True, violations=violations))
        else:
            results.append(LintResult(tool="tsc", available=False, violations=[], note="tsc not found in PATH"))

    return results


def _lint_go(file_path: str) -> list[LintResult]:
    results = []

    golangci = shutil.which("golangci-lint")
    if golangci:
        proc = _run_command([golangci, "run", "--out-format", "line-number", file_path])
        combined = f"{proc.stdout or ''}\n{proc.stderr or ''}" if proc is not None else ""
        violations = _parse_colon_diagnostics("golangci-lint", combined, code="GOLANGCI")
        results.append(LintResult(tool="golangci-lint", available=True, violations=violations))
    else:
        results.append(
            LintResult(tool="golangci-lint", available=False, violations=[], note="golangci-lint not found in PATH")
        )

    go_bin = shutil.which("go")
    if go_bin:
        proc = _run_command([go_bin, "vet", file_path])
        combined = f"{proc.stdout or ''}\n{proc.stderr or ''}" if proc is not None else ""
        violations = _parse_colon_diagnostics("go vet", combined, code="GOVET")
        results.append(LintResult(tool="go vet", available=True, violations=violations))
    else:
        results.append(LintResult(tool="go vet", available=False, violations=[], note="go not found in PATH"))

    return results


def _lint_rust(file_path: str) -> list[LintResult]:
    results = []
    rustc = shutil.which("rustc")
    if not rustc:
        return [LintResult(tool="rustc", available=False, violations=[], note="rustc not found in PATH")]

    proc = _run_command(
        [rustc, "--edition=2021", "--error-format=json", "--emit=metadata", file_path],
    )

    violations = []
    stream = (proc.stderr or "") if proc is not None else ""
    for line in stream.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("level") not in ("error", "warning"):
            continue
        spans = obj.get("spans", [])
        span = spans[0] if spans else {}
        violations.append(
            _build_violation(
                "rustc",
                obj.get("message", "Rust diagnostic"),
                span.get("line_start"),
                span.get("column_start"),
                code=str(obj.get("code", {}).get("code") or "RUSTC"),
            )
        )

    return [LintResult(tool="rustc", available=True, violations=violations)]


def _lint_java(file_path: str) -> list[LintResult]:
    javac = shutil.which("javac")
    if not javac:
        return [LintResult(tool="javac", available=False, violations=[], note="javac not found in PATH")]

    proc = _run_command([javac, "-Xlint:all", file_path])
    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}" if proc is not None else ""
    violations = _parse_colon_diagnostics("javac", combined, code="JAVAC")
    return [LintResult(tool="javac", available=True, violations=violations)]


def _lint_c_like(file_path: str, language: str) -> list[LintResult]:
    if language == "C++":
        compiler = shutil.which("clang++") or shutil.which("g++")
        tool_name = "clang++" if shutil.which("clang++") else "g++"
    else:
        compiler = shutil.which("clang") or shutil.which("gcc")
        tool_name = "clang" if shutil.which("clang") else "gcc"

    if not compiler:
        return [
            LintResult(
                tool=f"{language} compiler",
                available=False,
                violations=[],
                note=f"No {language} compiler found in PATH",
            )
        ]

    proc = _run_command([compiler, "-Wall", "-Wextra", "-fsyntax-only", file_path])
    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}" if proc is not None else ""
    violations = _parse_colon_diagnostics(tool_name, combined, code="COMPILER")
    return [LintResult(tool=tool_name, available=True, violations=violations)]


def analyze_external_linters(code_string: str, language: str = "Python") -> dict:
    normalized = normalize_language(language)
    if normalized == "Python":
        return {"violations": [], "tool_status": []}

    temp_dir, file_path = _write_temp_source(code_string, normalized)
    try:
        lint_results = []
        if normalized in ("JavaScript", "TypeScript"):
            lint_results = _lint_javascript_typescript(file_path, normalized)
        elif normalized == "Go":
            lint_results = _lint_go(file_path)
        elif normalized == "Rust":
            lint_results = _lint_rust(file_path)
        elif normalized == "Java":
            lint_results = _lint_java(file_path)
        elif normalized in ("C", "C++"):
            lint_results = _lint_c_like(file_path, normalized)

        merged = []
        seen = set()
        for result in lint_results:
            for issue in result.violations:
                key = (issue.get("tool"), issue.get("code"), issue.get("message"), issue.get("line"), issue.get("column"))
                if key in seen:
                    continue
                seen.add(key)
                merged.append(issue)

        tool_status = [
            {
                "tool": result.tool,
                "available": result.available,
                "issues": len(result.violations),
                "note": result.note,
            }
            for result in lint_results
        ]

        return {"violations": merged, "tool_status": tool_status}
    finally:
        _cleanup_temp_dir(temp_dir)

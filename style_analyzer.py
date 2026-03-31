import re
import subprocess
import sys
import tempfile
import os

from language_config import LANGUAGE_EXTENSIONS, normalize_language


_VIOLATION_RE = re.compile(r"^.*?:(\d+):(\d+):\s+([A-Z]\d+)\s+(.*)$")


def _analyze_python_pep8(code_string: str) -> list[dict]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as tmp:
        tmp.write(code_string)
        tmp_path = tmp.name

    try:
        cmd = [sys.executable, "-m", "pycodestyle", tmp_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    violations = []
    for line in result.stdout.splitlines():
        match = _VIOLATION_RE.match(line.strip())
        if not match:
            continue
        line_no, col_no, code, message = match.groups()
        violations.append(
            {
                "code": code,
                "message": message,
                "line": int(line_no),
                "column": int(col_no),
            }
        )

    return violations


def _analyze_generic_style(code_string: str, language: str) -> list[dict]:
    violations = []
    max_len = 120

    for line_no, line in enumerate(code_string.splitlines(), start=1):
        stripped = line.rstrip("\n")
        if len(stripped) > max_len:
            violations.append(
                {
                    "code": "STYLE_LINE_LEN",
                    "message": f"Line exceeds {max_len} characters",
                    "line": line_no,
                    "column": max_len + 1,
                }
            )
        if "\t" in line:
            violations.append(
                {
                    "code": "STYLE_TAB",
                    "message": "Tab indentation found; prefer spaces for consistent formatting",
                    "line": line_no,
                    "column": line.find("\t") + 1,
                }
            )
        if stripped != line and line.rstrip(" ") != line:
            violations.append(
                {
                    "code": "STYLE_TRAIL_WS",
                    "message": "Trailing whitespace",
                    "line": line_no,
                    "column": len(line.rstrip(" ")) + 1,
                }
            )

    if language in ("JavaScript", "TypeScript"):
        for line_no, line in enumerate(code_string.splitlines(), start=1):
            if "console.log(" in line:
                violations.append(
                    {
                        "code": "STYLE_CONSOLE",
                        "message": "console.log found; consider structured logging or removal in production code",
                        "line": line_no,
                        "column": line.find("console.log(") + 1,
                    }
                )

    return violations


def analyze_style(code_string: str, language: str = "Python") -> list[dict]:
    normalized = normalize_language(language)
    if normalized == "Python":
        return _analyze_python_pep8(code_string)
    return _analyze_generic_style(code_string, normalized)


def temp_file_suffix(language: str) -> str:
    normalized = normalize_language(language)
    return LANGUAGE_EXTENSIONS.get(normalized, ".txt")
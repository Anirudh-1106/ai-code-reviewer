import re
import subprocess
import sys
import tempfile
import os


_VIOLATION_RE = re.compile(r"^.*?:(\d+):(\d+):\s+([A-Z]\d+)\s+(.*)$")


def analyze_pep8(code_string: str) -> list[dict]:
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
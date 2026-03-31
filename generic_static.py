import re

from language_config import normalize_language

_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
_KEYWORDS = {
    "if", "else", "for", "while", "return", "switch", "case", "break", "continue",
    "class", "struct", "enum", "interface", "type", "function", "func", "def", "fn",
    "public", "private", "protected", "static", "const", "let", "var", "new", "import",
    "from", "package", "using", "namespace", "try", "catch", "finally", "throw", "async",
    "await", "true", "false", "null", "None", "this", "super", "self", "mut",
}

_COMMON_GLOBALS = {
    "JavaScript": {"console", "window", "document", "Math", "JSON", "Array", "Number", "String"},
    "TypeScript": {"console", "window", "document", "Math", "JSON", "Array", "Number", "String"},
    "Java": {"System", "String", "Integer", "Math"},
    "C++": {"std", "cout", "cin", "endl", "size_t"},
    "C": {"printf", "scanf", "size_t"},
    "Go": {"fmt", "len", "make", "append"},
    "Rust": {"println", "String", "Vec", "Option", "Result"},
}

_DECLARATION_PATTERNS = {
    "JavaScript": [
        re.compile(r"\b(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)"),
        re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
    ],
    "TypeScript": [
        re.compile(r"\b(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)"),
        re.compile(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
    ],
    "Java": [
        re.compile(
            r"\b(?:public|private|protected)?\s*(?:static\s+)?"
            r"(?:[A-Za-z_][A-Za-z0-9_<>\[\]]*\s+)+([A-Za-z_][A-Za-z0-9_]*)\s*\("
        ),
        re.compile(
            r"\b(?:int|long|float|double|boolean|char|String|var|final\s+[A-Za-z_][A-Za-z0-9_<>\[\]]*)\s+"
            r"([A-Za-z_][A-Za-z0-9_]*)"
        ),
    ],
    "C++": [
        re.compile(
            r"\b(?:[A-Za-z_][A-Za-z0-9_:<>]*\s+)+([A-Za-z_][A-Za-z0-9_]*)\s*\("
        ),
        re.compile(
            r"\b(?:int|long|float|double|bool|char|auto|std::string)\s+([A-Za-z_][A-Za-z0-9_]*)"
        ),
    ],
    "C": [
        re.compile(r"\b(?:[A-Za-z_][A-Za-z0-9_\*\s]*\s+)([A-Za-z_][A-Za-z0-9_]*)\s*\("),
        re.compile(r"\b(?:int|long|float|double|char|bool)\s+([A-Za-z_][A-Za-z0-9_]*)"),
    ],
    "Go": [
        re.compile(r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
        re.compile(r"\b(?:var|const)\s+([A-Za-z_][A-Za-z0-9_]*)"),
        re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*"),
    ],
    "Rust": [
        re.compile(r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
        re.compile(r"\blet\s+(?:mut\s+)?([A-Za-z_][A-Za-z0-9_]*)"),
    ],
}

_IMPORT_PATTERNS = {
    "JavaScript": [
        re.compile(r"\bimport\s+([A-Za-z_][A-Za-z0-9_]*)\s+from\b"),
        re.compile(r"\bimport\s+\{([^}]+)\}\s+from\b"),
    ],
    "TypeScript": [
        re.compile(r"\bimport\s+([A-Za-z_][A-Za-z0-9_]*)\s+from\b"),
        re.compile(r"\bimport\s+\{([^}]+)\}\s+from\b"),
    ],
    "Java": [re.compile(r"\bimport\s+([A-Za-z0-9_\.\*]+)\s*;")],
    "C++": [re.compile(r"#include\s+[<\"]([^>\"]+)[>\"]")],
    "C": [re.compile(r"#include\s+[<\"]([^>\"]+)[>\"]")],
    "Go": [re.compile(r"\bimport\s+\"([^\"]+)\""), re.compile(r"\bimport\s+\((.*?)\)", re.DOTALL)],
    "Rust": [re.compile(r"\buse\s+([A-Za-z0-9_:]+)")],
}


def _names_from_import_match(match: re.Match) -> list[str]:
    value = match.group(1).strip()
    if "," in value or "{" in value:
        chunks = [part.strip() for part in re.split(r",", value) if part.strip()]
        output = []
        for chunk in chunks:
            cleaned = chunk.replace("{", "").replace("}", "").strip()
            if cleaned:
                output.append(cleaned.split(" as ")[-1].strip())
        return output
    if "/" in value or "." in value or "::" in value:
        return [value.split("/")[-1].split(".")[0].split("::")[-1]]
    return [value]


def _collect_usages(code_string: str) -> set[str]:
    return {
        token
        for token in _IDENTIFIER_RE.findall(code_string)
        if token not in _KEYWORDS and not token.isupper()
    }


def _collect_declarations(code_string: str, language: str) -> list[dict]:
    declarations = []
    patterns = _DECLARATION_PATTERNS.get(language, [])
    for line_no, line in enumerate(code_string.splitlines(), start=1):
        for pattern in patterns:
            for match in pattern.finditer(line):
                name = match.group(1)
                declarations.append({"name": name, "line": line_no})
    return declarations


def _collect_imports(code_string: str, language: str) -> list[dict]:
    imports = []
    patterns = _IMPORT_PATTERNS.get(language, [])
    lines = code_string.splitlines()

    for line_no, line in enumerate(lines, start=1):
        for pattern in patterns:
            for match in pattern.finditer(line):
                for name in _names_from_import_match(match):
                    imports.append({"name": name, "module": name, "line": line_no})

    if language == "Go":
        joined = "\n".join(lines)
        block_match = re.search(r"\bimport\s*\((.*?)\)", joined, flags=re.DOTALL)
        if block_match:
            block = block_match.group(1)
            start_line = joined[:block_match.start()].count("\n") + 1
            for idx, raw in enumerate(block.splitlines(), start=1):
                path_match = re.search(r'"([^\"]+)"', raw)
                if path_match:
                    name = path_match.group(1).split("/")[-1]
                    imports.append(
                        {"name": name, "module": path_match.group(1), "line": start_line + idx}
                    )

    unique = []
    seen = set()
    for item in imports:
        key = (item["name"], item["line"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _collect_function_params(code_string: str, language: str) -> set[str]:
    params = set()

    if language in ("JavaScript", "TypeScript"):
        pattern = re.compile(r"\bfunction\s+[A-Za-z_][A-Za-z0-9_]*\s*\(([^)]*)\)")
        for match in pattern.finditer(code_string):
            for token in match.group(1).split(","):
                name = token.strip().split(":")[0].strip()
                if name:
                    params.add(name)

    if language == "Python":
        pattern = re.compile(r"\bdef\s+[A-Za-z_][A-Za-z0-9_]*\s*\(([^)]*)\)")
        for match in pattern.finditer(code_string):
            for token in match.group(1).split(","):
                name = token.strip().split(":")[0].split("=")[0].strip()
                if name:
                    params.add(name)

    if language in ("Java", "C++", "C", "Go", "Rust"):
        pattern = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\(([^)]*)\)")
        for match in pattern.finditer(code_string):
            for token in match.group(1).split(","):
                token = token.strip()
                if not token:
                    continue
                name = token.split()[-1].replace("*", "").replace("&", "")
                name = name.split(":")[-1].strip()
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
                    params.add(name)

    return params


def generic_report_unused(code_string: str, language: str) -> dict:
    normalized = normalize_language(language)
    declarations = _collect_declarations(code_string, normalized)
    imports = _collect_imports(code_string, normalized)
    usages = _collect_usages(code_string)

    unused_imports = [item for item in imports if item["name"] not in usages]

    function_like = []
    variable_like = []
    for item in declarations:
        line = code_string.splitlines()[max(item["line"] - 1, 0)] if code_string else ""
        if "(" in line and ")" in line:
            function_like.append(item)
        else:
            variable_like.append(item)

    unused_functions = [item for item in function_like if item["name"] not in usages]
    unused_variables = [item for item in variable_like if item["name"] not in usages]

    return {
        "unused_imports": unused_imports,
        "unused_variables": unused_variables,
        "unused_functions": unused_functions,
    }


def generic_variable_context(code_string: str, language: str) -> dict:
    normalized = normalize_language(language)
    declarations = _collect_declarations(code_string, normalized)
    usages = _collect_usages(code_string)

    used = []
    for line_no, line in enumerate(code_string.splitlines(), start=1):
        for token in _IDENTIFIER_RE.findall(line):
            if token in usages and token not in _KEYWORDS:
                used.append({"name": token, "line": line_no})

    return {
        "created": declarations,
        "used": used,
    }


def generic_undefined_identifiers(code_string: str, language: str) -> list[str]:
    normalized = normalize_language(language)
    declarations = _collect_declarations(code_string, normalized)
    imports = _collect_imports(code_string, normalized)
    params = _collect_function_params(code_string, normalized)

    defined = {item["name"] for item in declarations}
    defined.update(item["name"] for item in imports)
    defined.update(params)
    defined.update(_COMMON_GLOBALS.get(normalized, set()))

    issues = []
    seen = set()
    for line_no, line in enumerate(code_string.splitlines(), start=1):
        for token in _IDENTIFIER_RE.findall(line):
            if token in _KEYWORDS or token in defined:
                continue
            if token[:1].isupper():
                continue
            key = (token, line_no)
            if key in seen:
                continue
            seen.add(key)
            if re.search(rf"\b{re.escape(token)}\s*\(", line):
                continue
            issues.append(f"Possibly undefined identifier: {token} (line {line_no})")
    return issues

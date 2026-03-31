import ast

from language_config import TREE_SITTER_LANGUAGE_NAMES, normalize_language


def _python_parse(code_string: str) -> dict:
    try:
        ast.parse(code_string)
        return {"success": True, "error": None}
    except SyntaxError as error:
        return {
            "success": False,
            "error": {
                "message": f"Syntax Error: {error.msg}",
                "line": error.lineno,
                "column": error.offset,
            },
        }


def _tree_sitter_parse(code_string: str, language: str) -> dict:
    try:
        from tree_sitter_languages import get_parser
    except Exception:
        return {
            "success": True,
            "error": None,
            "warning": "tree-sitter parser unavailable; syntax check skipped for selected language.",
        }

    parser_name = TREE_SITTER_LANGUAGE_NAMES.get(language)
    if not parser_name:
        return {"success": True, "error": None}

    try:
        parser = get_parser(parser_name)
        tree = parser.parse(code_string.encode("utf-8"))
    except Exception as error:
        return {
            "success": True,
            "error": None,
            "warning": f"Parser setup warning for {language}: {error}. Syntax check skipped.",
        }

    if not tree.root_node.has_error:
        return {"success": True, "error": None}

    error_node = next(
        (node for node in tree.root_node.children if node.type == "ERROR"),
        None,
    )
    if error_node is None:
        return {
            "success": False,
            "error": {
                "message": "Syntax Error: tree-sitter detected invalid syntax.",
                "line": None,
                "column": None,
            },
        }

    return {
        "success": False,
        "error": {
            "message": f"Syntax Error near '{error_node.type}'",
            "line": error_node.start_point[0] + 1,
            "column": error_node.start_point[1] + 1,
        },
    }


def parse_code(code_string: str, language: str = "Python") -> dict:
    normalized = normalize_language(language)
    if normalized == "Python":
        return _python_parse(code_string)
    return _tree_sitter_parse(code_string, normalized)

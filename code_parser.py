import ast

def parse_code(code_string: str):
    """
    Parse Python code and report syntax errors with line number.
    """
    try:
        ast.parse(code_string)
        return {
            "success": True,
            "error": None
        }

    except SyntaxError as e:
        return {
            "success": False,
            "error": {
                "message": f"Syntax Error: {e.msg}",
                "line": e.lineno,
                "column": e.offset
            }
        }

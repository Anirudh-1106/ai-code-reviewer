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


# Demo input (same style as mam)
if __name__ == "__main__":
    code = parse_code("""
def calculate_sum(a, b):
    result = a + b
    if result > 10:
        print("Greater than 10")
    else:
        print("Less than or equal to 10")
    return result
""")

    print(code)

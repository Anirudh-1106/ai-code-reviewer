import ast

from generic_static import generic_variable_context
from language_config import normalize_language

class VariableContextTracker(ast.NodeVisitor):
    def __init__(self):
        self.created = []
        self.used = []

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.created.append({"name": node.id, "line": node.lineno})
        elif isinstance(node.ctx, ast.Load):
            self.used.append({"name": node.id, "line": node.lineno})
        self.generic_visit(node)


def track_variable_context(code_string: str, language: str = "Python") -> dict:
    normalized = normalize_language(language)
    if normalized != "Python":
        return generic_variable_context(code_string, normalized)

    tree = ast.parse(code_string)
    visitor = VariableContextTracker()
    visitor.visit(tree)
    return {
        "created": visitor.created,
        "used": visitor.used,
    }
import ast

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


def track_variable_context(code_string: str) -> dict:
    tree = ast.parse(code_string)
    visitor = VariableContextTracker()
    visitor.visit(tree)
    return {
        "created": visitor.created,
        "used": visitor.used,
    }
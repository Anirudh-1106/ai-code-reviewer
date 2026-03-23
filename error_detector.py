import ast


class AIReviewer(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
        self.variable_defs = []
        self.function_defs = []
        self.used_names = set()
        self.called_functions = set()

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split(".")[0]
            self.imports.append(
                {
                    "name": name,
                    "module": alias.name,
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module or ""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            full_module = f"{module}.{alias.name}" if module else alias.name
            self.imports.append(
                {
                    "name": name,
                    "module": full_module,
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.function_defs.append(
            {
                "name": node.name,
                "line": node.lineno,
            }
        )
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.variable_defs.append(
                {
                    "name": node.id,
                    "line": node.lineno,
                }
            )
        elif isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called_functions.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called_functions.add(node.func.attr)
        self.generic_visit(node)


def report_unused(code_string: str) -> dict:
    tree = ast.parse(code_string)
    reviewer = AIReviewer()
    reviewer.visit(tree)

    unused_imports = [
        item for item in reviewer.imports if item["name"] not in reviewer.used_names
    ]

    function_names = {item["name"] for item in reviewer.function_defs}
    unused_variables = [
        item
        for item in reviewer.variable_defs
        if item["name"] not in reviewer.used_names and item["name"] not in function_names
    ]

    unused_functions = [
        item
        for item in reviewer.function_defs
        if item["name"] not in reviewer.called_functions
    ]

    return {
        "unused_imports": unused_imports,
        "unused_variables": unused_variables,
        "unused_functions": unused_functions,
    }
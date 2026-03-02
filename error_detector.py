import ast

code = '''
import os
import sys
from datetime import datetime, timedelta
score = 100
print(score)
'''

class AIReviewer(ast.NodeVisitor):

    def __init__(self):
        self.defined = set()
        self.used = set()

    # Track normal imports
    def visit_Import(self, node):
        for alias in node.names:
            print(alias)
            print(alias.name)
            self.defined.add(alias.name)
        self.generic_visit(node)

    # Track from-imports
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.defined.add(alias.name)
        self.generic_visit(node)

    # Track variables
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used.add(node.id)
        self.generic_visit(node)

    # Final report
    def report_unused(self):
        unused = self.defined - self.used

        print("--- AI REVIEW REPORT ---")
        if not unused:
            print("Everything is used! Good job bro!")
        else:
            for item in unused:
                print(f"UNUSED ITEM FOUND: {item}")


# Execution
tree = ast.parse(code)
reviewer = AIReviewer()
reviewer.visit(tree)
reviewer.report_unused()
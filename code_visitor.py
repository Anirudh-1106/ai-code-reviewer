import ast

#code = 
'''
import os
import sys
from datetime import datetime, timedelta
'''

'''class ImportFinder(ast.NodeVisitor):
    def visit_Import(self, node):
        for alias in node.names:
            print(f'Found import: {alias.name}')
        self.generic_visit(node) 

    def visit_ImportFrom(self, node):
        print(f'Found import from: {node.module}')
         #self.generic_visit(node)

tree = ast.parse(code)
visitor = ImportFinder()

visitor.visit(tree)'''
class VariableContextTracker(ast.NodeVisitor):
    def visit_Name(self, node):
        if isinstance(node.ctx,ast.Store):
            print(f'Variable {node.id} is being created on line {node.lineno}')
        elif isinstance(node.ctx, ast.Load):
            print(f'Variable {node.id} is being used on line {node.lineno}')
        self.generic_visit(node)
code = '''
x=100
print(x)'''
tree = ast.parse(code)
print(ast.dump(tree, indent=4))
visitor=VariableContextTracker()
visitor.visit(tree)
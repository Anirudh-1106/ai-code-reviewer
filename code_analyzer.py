import builtins
import ast
import difflib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_suggestor import get_ai_review
from code_parser import parse_code
from code_visitor import track_variable_context
from error_detector import report_unused


def _static_issue_strings(issues: dict) -> list:
    output = []
    for item in issues.get("unused_imports", []):
        output.append(f"Unused import: {item.get('name', 'unknown')}")
    for item in issues.get("unused_variables", []):
        output.append(f"Unused variable: {item.get('name', 'unknown')}")
    for item in issues.get("unused_functions", []):
        output.append(f"Unused function: {item.get('name', 'unknown')}")
    return output


def _merge_issue_lists(static_issues: list, ai_issues: list) -> list:
    merged = []
    seen = set()
    for item in static_issues + ai_issues:
        text = str(item).strip()
        if not text:
            continue
        key = text.lower()
        if key not in seen:
            seen.add(key)
            merged.append(text)
    return merged


class _ScopeAwareUndefinedNameVisitor(ast.NodeVisitor):
    def __init__(self):
        self.builtins = set(dir(builtins))
        self.scope_stack = [set(self.builtins)]
        self.undefined = []
        self._seen = set()

    def _push_scope(self, initial=None):
        self.scope_stack.append(set(initial or []))

    def _pop_scope(self):
        self.scope_stack.pop()

    def _define(self, name: str):
        if name:
            self.scope_stack[-1].add(name)

    def _is_defined(self, name: str) -> bool:
        if not name:
            return True
        if name.startswith("__") and name.endswith("__"):
            return True
        for scope in reversed(self.scope_stack):
            if name in scope:
                return True
        return False

    def _collect_target_names(self, node):
        names = []
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for elt in node.elts:
                names.extend(self._collect_target_names(elt))
        elif isinstance(node, ast.Starred):
            names.extend(self._collect_target_names(node.value))
        return names

    def _mark_undefined(self, name: str, line):
        if self._is_defined(name):
            return
        key = (name, line)
        if key in self._seen:
            return
        self._seen.add(key)
        self.undefined.append(f"Undefined variable: {name} (line {line})")

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self._mark_undefined(node.id, getattr(node, "lineno", "?"))
        elif isinstance(node.ctx, ast.Store):
            self._define(node.id)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self._define(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == "*":
                continue
            self._define(alias.asname or alias.name)

    def visit_Assign(self, node):
        self.visit(node.value)
        for target in node.targets:
            for name in self._collect_target_names(target):
                self._define(name)

    def visit_AnnAssign(self, node):
        if node.value is not None:
            self.visit(node.value)
        if node.annotation is not None:
            self.visit(node.annotation)
        for name in self._collect_target_names(node.target):
            self._define(name)

    def visit_AugAssign(self, node):
        self.visit(node.target)
        self.visit(node.value)
        for name in self._collect_target_names(node.target):
            self._define(name)

    def visit_For(self, node):
        self.visit(node.iter)
        for name in self._collect_target_names(node.target):
            self._define(name)
        for stmt in node.body:
            self.visit(stmt)
        for stmt in node.orelse:
            self.visit(stmt)

    def visit_With(self, node):
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars is not None:
                for name in self._collect_target_names(item.optional_vars):
                    self._define(name)
        for stmt in node.body:
            self.visit(stmt)

    def visit_ExceptHandler(self, node):
        if node.type is not None:
            self.visit(node.type)
        if node.name:
            self._define(node.name)
        for stmt in node.body:
            self.visit(stmt)

    def visit_FunctionDef(self, node):
        self._define(node.name)

        for decorator in node.decorator_list:
            self.visit(decorator)
        for arg in list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs):
            if arg.annotation is not None:
                self.visit(arg.annotation)
        if node.args.vararg and node.args.vararg.annotation is not None:
            self.visit(node.args.vararg.annotation)
        if node.args.kwarg and node.args.kwarg.annotation is not None:
            self.visit(node.args.kwarg.annotation)
        if node.returns is not None:
            self.visit(node.returns)
        for default in list(node.args.defaults) + list(node.args.kw_defaults):
            if default is not None:
                self.visit(default)

        func_scope_names = [
            arg.arg for arg in (list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs))
        ]
        if node.args.vararg:
            func_scope_names.append(node.args.vararg.arg)
        if node.args.kwarg:
            func_scope_names.append(node.args.kwarg.arg)

        self._push_scope(func_scope_names)
        for stmt in node.body:
            self.visit(stmt)
        self._pop_scope()

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self._define(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword)

        self._push_scope()
        for stmt in node.body:
            self.visit(stmt)
        self._pop_scope()


def _undefined_variable_strings(code_string: str) -> list:
    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        return []

    visitor = _ScopeAwareUndefinedNameVisitor()
    visitor.visit(tree)
    return visitor.undefined


def _normalize_improved_code(value, original_code: str) -> str:
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return original_code
        if (
            cleaned.startswith("{")
            and cleaned.endswith("}")
            and ('"import ' in cleaned or "'import " in cleaned)
        ):
            return original_code
        return value

    if isinstance(value, (list, tuple)):
        if value and all(isinstance(item, str) for item in value):
            joined = "\n".join(value).strip()
            return joined if joined else original_code
        return original_code

    if isinstance(value, dict):
        for key in ("improved_code", "code", "refactored_code"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate
        return original_code

    return original_code


def analyze_code_pipeline(code_string: str, language: str = "Python") -> dict:
    parse_result = parse_code(code_string)
    if not parse_result.get("success", False):
        error_obj = parse_result.get("error", {})
        message = error_obj.get("message", "Syntax error")
        return {"error": message, "success": False}

    issues = report_unused(code_string)
    variable_context = track_variable_context(code_string)
    ai_review = get_ai_review(code_string, issues, language)
    if not isinstance(ai_review, dict):
        ai_review = {
            "quality_grade": "N/A",
            "analysis_summary": "Parse error",
            "issues_found": [],
            "improved_code": code_string,
            "detailed_explanations": {},
            "ai_fallback": True,
        }

    improved_code = _normalize_improved_code(
        ai_review.get("improved_code", code_string), code_string
    )

    static_issues = _static_issue_strings(issues)
    static_issues += _undefined_variable_strings(code_string)
    ai_issues = ai_review.get("issues_found", [])
    if not isinstance(ai_issues, list):
        ai_issues = [str(ai_issues)]
    merged_issues = _merge_issue_lists(static_issues, ai_issues)

    original_lines = code_string.splitlines()
    improved_lines = improved_code.splitlines()

    raw_diff = list(
        difflib.unified_diff(
            original_lines,
            improved_lines,
            fromfile="original",
            tofile="improved",
            lineterm="",
        )
    )

    diff_lines = []
    for idx, line in enumerate(raw_diff, start=1):
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            line_type = "add"
        elif line.startswith("-"):
            line_type = "remove"
        else:
            line_type = "equal"
        diff_lines.append({"type": line_type, "line": line, "num": idx})

    return {
        "success": True,
        "quality_grade": ai_review.get("quality_grade", "N/A"),
        "issues_count": len(merged_issues),
        "analysis_summary": ai_review.get("analysis_summary", ""),
        "original_code": code_string,
        "improved_code": improved_code,
        "issues_found": merged_issues,
        "detailed_explanations": ai_review.get("detailed_explanations", {}),
        "ai_fallback": bool(ai_review.get("ai_fallback", False)),
        "static_analysis": issues,
        "variable_context": variable_context,
        "diff_lines": diff_lines,
    }

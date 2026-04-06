from datetime import datetime
from io import BytesIO
import textwrap

import reflex as rx
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from ai_suggestor import ask_ai_assistant
from code_analyzer import analyze_code_pipeline
from language_config import LANGUAGE_DEMOS, supported_languages


class ReviewerState(rx.State):
    code_input: str = ""
    selected_language: str = "Python"
    quality_grade: str = "N/A"
    issues_count: int = 0
    analysis_summary: str = ""
    improved_code: str = ""
    original_code: str = ""
    issues_found: list[str] = []
    unused_imports: list[str] = []
    unused_functions: list[str] = []
    unused_variables: list[str] = []
    style_violations: list[str] = []
    external_linter_violations: list[str] = []
    external_linter_tool_status: list[str] = []
    created_variables: list[str] = []
    used_variables: list[str] = []
    history_entries: list[dict[str, str]] = []
    selected_history_id: str = ""
    assistant_prompt: str = ""
    assistant_messages: list[dict[str, str]] = []
    error_message: str = ""
    ai_fallback: bool = False

    @staticmethod
    def _severity_for_issue(issue: str) -> str:
        text = issue.lower()
        critical_terms = [
            "vulnerability",
            "security",
            "injection",
            "xss",
            "critical",
            "rce",
            "out-of-bounds",
        ]
        high_terms = [
            "error",
            "undefined",
            "failed",
            "exception",
            "missing",
            "not found",
            "syntax",
        ]
        medium_terms = [
            "unused",
            "style",
            "complexity",
            "performance",
            "warning",
            "lint",
        ]
        low_terms = [
            "best practice",
            "readability",
            "documentation",
            "comment",
        ]

        if any(term in text for term in critical_terms):
            return "Critical"
        if any(term in text for term in high_terms):
            return "High"
        if any(term in text for term in medium_terms):
            return "Medium"
        if any(term in text for term in low_terms):
            return "Low"
        return "Info"

    @staticmethod
    def _severity_style(severity: str) -> dict:
        palette = {
            "Critical": {
                "fg": "#fecaca",
                "bg": "rgba(127, 29, 29, 0.42)",
                "border": "1px solid rgba(248, 113, 113, 0.52)",
            },
            "High": {
                "fg": "#fed7aa",
                "bg": "rgba(124, 45, 18, 0.38)",
                "border": "1px solid rgba(251, 146, 60, 0.45)",
            },
            "Medium": {
                "fg": "#fde68a",
                "bg": "rgba(113, 63, 18, 0.35)",
                "border": "1px solid rgba(245, 158, 11, 0.44)",
            },
            "Low": {
                "fg": "#bfdbfe",
                "bg": "rgba(30, 64, 175, 0.28)",
                "border": "1px solid rgba(96, 165, 250, 0.42)",
            },
            "Info": {
                "fg": "#c4b5fd",
                "bg": "rgba(67, 56, 202, 0.25)",
                "border": "1px solid rgba(139, 92, 246, 0.4)",
            },
        }
        return palette.get(severity, palette["Info"])

    @rx.var
    def severity_breakdown(self) -> list[dict]:
        order = ["Critical", "High", "Medium", "Low", "Info"]
        counts = {key: 0 for key in order}

        for issue in self.issues_found:
            severity = self._severity_for_issue(issue)
            counts[severity] += 1

        output = []
        for severity in order:
            count = counts[severity]
            if count <= 0:
                continue
            style = self._severity_style(severity)
            output.append(
                {
                    "severity": severity,
                    "count": str(count),
                    "fg": style["fg"],
                    "bg": style["bg"],
                    "border": style["border"],
                }
            )
        return output

    @rx.var
    def grouped_external_issues(self) -> list[str]:
        external = []
        external_terms = [
            "eslint",
            "tsc",
            "golangci",
            "go vet",
            "rustc",
            "javac",
            "compiler",
        ]

        for issue in self.issues_found:
            text = issue.lower()
            if any(term in text for term in external_terms):
                external.append(issue)
        return external

    @rx.var
    def grouped_static_issues(self) -> list[str]:
        static = []
        external_terms = [
            "eslint",
            "tsc",
            "golangci",
            "go vet",
            "rustc",
            "javac",
            "compiler",
        ]

        for issue in self.issues_found:
            text = issue.lower()
            if any(term in text for term in external_terms):
                continue
            if (
                "unused" in text
                or "undefined" in text
                or "style" in text
                or "lint" in text
                or "syntax" in text
            ):
                static.append(issue)
        return static

    @rx.var
    def grouped_ai_issues(self) -> list[str]:
        ai = []
        external_terms = [
            "eslint",
            "tsc",
            "golangci",
            "go vet",
            "rustc",
            "javac",
            "compiler",
        ]

        for issue in self.issues_found:
            text = issue.lower()
            if any(term in text for term in external_terms):
                continue
            if (
                "unused" in text
                or "undefined" in text
                or "style" in text
                or "lint" in text
                or "syntax" in text
            ):
                continue
            ai.append(issue)
        return ai

    def update_code_input(self, value: str) -> None:
        self.code_input = value

    @rx.var
    def available_languages(self) -> list[str]:
        return supported_languages()

    def update_language(self, value: str) -> None:
        self.selected_language = value

    def load_demo(self) -> None:
        self.code_input = LANGUAGE_DEMOS.get(self.selected_language, LANGUAGE_DEMOS["Python"])

    @rx.var
    def original_code_with_lines(self) -> str:
        lines = self.original_code.splitlines()
        return "\n".join(f"{idx + 1:>3} | {line}" for idx, line in enumerate(lines))

    @rx.var
    def improved_code_with_lines(self) -> str:
        lines = self.improved_code.splitlines()
        return "\n".join(f"{idx + 1:>3} | {line}" for idx, line in enumerate(lines))

    def _build_report_text(self) -> str:
        issues_text = "\n".join(f"- {item}" for item in self.issues_found)
        if not issues_text:
            issues_text = "- None"

        return (
            f"Code Review Report\n\n"
            f"Language: {self.selected_language}\n"
            f"Quality Grade: {self.quality_grade}\n"
            f"Issues Found: {self.issues_count}\n\n"
            f"Analysis Summary\n"
            f"{self.analysis_summary}\n\n"
            f"Issues\n"
            f"{issues_text}\n\n"
            f"Improved Code\n"
            f"{self.improved_code}\n"
        )

    def _build_pdf_report_bytes(self, report_text: str) -> bytes:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=LETTER)
        _, page_height = LETTER

        margin_x = 42
        margin_top = 50
        margin_bottom = 42
        chars_per_line = 100

        text_obj = pdf.beginText(margin_x, page_height - margin_top)
        text_obj.setFont("Helvetica", 10)

        for raw_line in report_text.splitlines():
            wrapped_lines = textwrap.wrap(raw_line, width=chars_per_line) or [""]
            for line in wrapped_lines:
                if text_obj.getY() <= margin_bottom:
                    pdf.drawText(text_obj)
                    pdf.showPage()
                    text_obj = pdf.beginText(margin_x, page_height - margin_top)
                    text_obj.setFont("Helvetica", 10)
                text_obj.textLine(line)

        pdf.drawText(text_obj)
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()

    def download_pdf_report(self):
        if not self.original_code.strip() and not self.improved_code.strip():
            self.error_message = "Run analysis first to generate a report."
            return

        report_text = self._build_report_text()
        pdf_bytes = self._build_pdf_report_bytes(report_text)
        filename = f"review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return rx.download(data=pdf_bytes, filename=filename, mime_type="application/pdf")

    def analyze(self) -> None:
        self.error_message = ""
        if not self.code_input.strip():
            self.error_message = "Please paste some code first."
            return

        result = analyze_code_pipeline(self.code_input, self.selected_language)
        if not result.get("success", False):
            self.error_message = result.get("error", "Analysis failed.")
            return

        self.quality_grade = str(result.get("quality_grade", "N/A"))
        self.issues_count = int(result.get("issues_count", 0))
        self.analysis_summary = str(result.get("analysis_summary", ""))
        self.original_code = str(result.get("original_code", ""))
        self.improved_code = str(result.get("improved_code", ""))
        self.issues_found = [str(item) for item in result.get("issues_found", [])]
        self.ai_fallback = bool(result.get("ai_fallback", False))

        static = result.get("static_analysis", {})
        self.unused_imports = [
            f"{item.get('name', 'unknown')} (from {item.get('module', 'unknown')}) - line {item.get('line', '?')}"
            for item in static.get("unused_imports", [])
        ]
        self.unused_functions = [
            f"{item.get('name', 'unknown')} - line {item.get('line', '?')}"
            for item in static.get("unused_functions", [])
        ]
        self.unused_variables = [
            f"{item.get('name', 'unknown')} - line {item.get('line', '?')}"
            for item in static.get("unused_variables", [])
        ]
        self.style_violations = [
            f"{item.get('code', 'STYLE')} - {item.get('message', 'Style violation')} "
            f"(line {item.get('line', '?')}, col {item.get('column', '?')})"
            for item in static.get("style_violations", [])
        ]
        self.external_linter_violations = [
            f"{item.get('tool', 'linter')} {item.get('code', 'LINT')} - {item.get('message', 'Issue')} "
            f"(line {item.get('line', '?')}, col {item.get('column', '?')})"
            for item in static.get("external_linter_violations", [])
        ]
        self.external_linter_tool_status = [
            (
                f"{item.get('tool', 'tool')}: "
                f"{'available' if item.get('available', False) else 'not available'}"
                f" | issues: {item.get('issues', 0)}"
                f"{(' | ' + str(item.get('note'))) if item.get('note') else ''}"
            )
            for item in static.get("external_linter_tool_status", [])
        ]

        variable_context = result.get("variable_context", {})
        self.created_variables = [
            f"{item.get('name', 'unknown')} - line {item.get('line', '?')}"
            for item in variable_context.get("created", [])
        ]
        self.used_variables = [
            f"{item.get('name', 'unknown')} - line {item.get('line', '?')}"
            for item in variable_context.get("used", [])
        ]

        snippet = self.code_input.strip().replace("\n", " ")[:80]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        record_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

        history_record = {
            "id": record_id,
            "summary": (
                f"{timestamp} | {self.selected_language} | Grade: {self.quality_grade} | "
                f"Issues: {self.issues_count} | {snippet}"
            ),
            "timestamp": timestamp,
            "language": self.selected_language,
            "grade": self.quality_grade,
            "issues_count": str(self.issues_count),
            "analysis_summary": self.analysis_summary,
            "original_code": self.original_code,
            "improved_code": self.improved_code,
            "issues_found": "\n".join(self.issues_found),
        }
        self.history_entries = [history_record] + self.history_entries

    def clear_history(self) -> None:
        self.history_entries = []
        self.selected_history_id = ""

    def toggle_history_entry(self, record_id: str) -> None:
        if self.selected_history_id == record_id:
            self.selected_history_id = ""
        else:
            self.selected_history_id = record_id

    def update_assistant_prompt(self, value: str) -> None:
        self.assistant_prompt = value

    def clear_assistant_chat(self) -> None:
        self.assistant_messages = []

    def send_assistant_message(self) -> None:
        prompt = self.assistant_prompt.strip()
        if not prompt:
            return

        chat_history = [
            {"role": item.get("role", ""), "content": item.get("content", "")}
            for item in self.assistant_messages
            if item.get("role") in ("user", "assistant")
        ]

        code_context = str(
            {
                "quality_grade": self.quality_grade,
                "issues_count": self.issues_count,
                "analysis_summary": self.analysis_summary,
                "issues_found": self.issues_found,
                "original_code": self.original_code,
                "improved_code": self.improved_code,
            }
        )

        response = ask_ai_assistant(prompt, code_context, chat_history)

        self.assistant_messages = self.assistant_messages + [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": str(response)},
        ]
        self.assistant_prompt = ""

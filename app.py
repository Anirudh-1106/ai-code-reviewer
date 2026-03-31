from datetime import datetime
import difflib
from io import BytesIO
import os
import sys
import textwrap

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_suggestor import ask_ai_assistant
from code_analyzer import analyze_code_pipeline
from language_config import normalize_language, supported_languages

st.set_page_config(page_title="AI Code Reviewer", layout="wide")

if "page" not in st.session_state:
    st.session_state["page"] = "💻 Code Editor"
if "language" not in st.session_state:
    st.session_state["language"] = "Python"
if "result" not in st.session_state:
    st.session_state["result"] = {}
if "code_input" not in st.session_state:
    st.session_state["code_input"] = ""
if "history" not in st.session_state:
    st.session_state["history"] = []
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []


def _build_markdown_report(result: dict) -> str:
    language = result.get("language", st.session_state.get("language", "Python"))
    lang_tag = str(language).lower()
    return f"""# Code Review Report
**Language:** {language}
**Quality Grade:** {result.get('quality_grade','N/A')}
**Issues Found:** {result.get('issues_count',0)}

## Analysis Summary
{result.get('analysis_summary','')}

## Issues Found
{chr(10).join(['- ' + i for i in result.get('issues_found',[])])}

## Improved Code
```{lang_tag}
{result.get('improved_code','')}
```

## Detailed Explanations
### Scalability Impact
{result.get('detailed_explanations',{}).get('scalability_impact','')}

### Time/Space Complexity
{result.get('detailed_explanations',{}).get('time_space_complexity','')}

### Security Vulnerabilities
{result.get('detailed_explanations',{}).get('security_vulnerabilities','')}

### Best Practices
{result.get('detailed_explanations',{}).get('best_practices','')}
"""


def _build_pdf_report_bytes(report_text: str) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    margin_x = 42
    margin_top = 50
    margin_bottom = 42
    chars_per_line = 100

    text_obj = pdf.beginText(margin_x, height - margin_top)
    text_obj.setFont("Helvetica", 10)

    for raw_line in report_text.splitlines():
        wrapped_lines = textwrap.wrap(raw_line, width=chars_per_line) or [""]
        for line in wrapped_lines:
            if text_obj.getY() <= margin_bottom:
                pdf.drawText(text_obj)
                pdf.showPage()
                text_obj = pdf.beginText(margin_x, height - margin_top)
                text_obj.setFont("Helvetica", 10)
            text_obj.textLine(line)

    pdf.drawText(text_obj)
    pdf.save()

    buffer.seek(0)
    return buffer.getvalue()


def render_top_nav() -> None:
    items = [
        "💻 Code Editor",
        "📊 Analysis Report",
        "🤖 AI Assistant",
        "📜 History",
    ]
    current_page = st.session_state.get("page", "💻 Code Editor")
    selected = st.radio(
        "Top Navigation",
        items,
        index=items.index(current_page),
        horizontal=True,
        label_visibility="collapsed",
        key="top_navigation",
    )
    if selected != current_page:
        st.session_state["page"] = selected
        st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace(" ", "&nbsp;")
    )


def _line_box_html(line_no: str, text: str, kind: str) -> str:
    if kind == "add":
        bg = "#d5f5dc"
        color = "#1f5e31"
    elif kind == "remove":
        bg = "#f8d1d1"
        color = "#7e1f1f"
    elif kind == "changed":
        bg = "#f3e7bf"
        color = "#5f4a00"
    else:
        bg = "#ffffff"
        color = "#2f2f2f"

    safe_text = _escape_html(text)
    safe_line = _escape_html(line_no)
    return (
        f'<div style="font-family:Consolas,monospace;font-size:16px;background:{bg};'
        f'padding:1px 8px;border-bottom:1px solid #d2d2d2;white-space:pre;line-height:1.35">'
        f'<span style="color:#4f4f4f;display:inline-block;min-width:42px">{safe_line}</span>'
        f'<span style="color:{color}">{safe_text}</span></div>'
    )


def render_side_by_side_diff(original_code: str, improved_code: str) -> None:
    orig_lines = original_code.splitlines()
    impr_lines = improved_code.splitlines()
    matcher = difflib.SequenceMatcher(a=orig_lines, b=impr_lines)

    left_rows = []
    right_rows = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for o_idx, i_idx in zip(range(i1, i2), range(j1, j2)):
                left_rows.append((str(o_idx + 1), orig_lines[o_idx], "equal"))
                right_rows.append((str(i_idx + 1), impr_lines[i_idx], "equal"))
        elif tag == "replace":
            left_block = orig_lines[i1:i2]
            right_block = impr_lines[j1:j2]
            block_matcher = difflib.SequenceMatcher(a=left_block, b=right_block)
            for btag, bi1, bi2, bj1, bj2 in block_matcher.get_opcodes():
                if btag == "equal":
                    for lk, rk in zip(range(bi1, bi2), range(bj1, bj2)):
                        left_rows.append((str(i1 + lk + 1), left_block[lk], "equal"))
                        right_rows.append((str(j1 + rk + 1), right_block[rk], "equal"))
                elif btag == "replace":
                    span = max(bi2 - bi1, bj2 - bj1)
                    for k in range(span):
                        if bi1 + k < bi2:
                            left_rows.append((str(i1 + bi1 + k + 1), left_block[bi1 + k], "remove"))
                        else:
                            left_rows.append(("", "", "equal"))
                        if bj1 + k < bj2:
                            right_rows.append((str(j1 + bj1 + k + 1), right_block[bj1 + k], "add"))
                        else:
                            right_rows.append(("", "", "equal"))
                elif btag == "delete":
                    for lk in range(bi1, bi2):
                        left_rows.append((str(i1 + lk + 1), left_block[lk], "remove"))
                        right_rows.append(("", "", "equal"))
                elif btag == "insert":
                    for rk in range(bj1, bj2):
                        left_rows.append(("", "", "equal"))
                        right_rows.append((str(j1 + rk + 1), right_block[rk], "add"))
        elif tag == "delete":
            for o_idx in range(i1, i2):
                left_rows.append((str(o_idx + 1), orig_lines[o_idx], "remove"))
                right_rows.append(("", "", "equal"))
        elif tag == "insert":
            for i_idx in range(j1, j2):
                left_rows.append(("", "", "equal"))
                right_rows.append((str(i_idx + 1), impr_lines[i_idx], "add"))

    if original_code.strip() == improved_code.strip():
        st.info("No code changes suggested in this run. Original and Improved are identical.")

    left_html = "".join(_line_box_html(line_no, text, kind) for line_no, text, kind in left_rows)
    right_html = "".join(
        _line_box_html(line_no, text, kind) for line_no, text, kind in right_rows
    )

    st.markdown(
        f"""
        <div style="display:grid;grid-template-columns:50% 50%;gap:0;border:1px solid #8f8f8f;border-radius:4px;overflow:hidden;background:#d9d9d9;width:100%;">
            <div style="border-right:1px solid #8f8f8f;min-width:0;">
                <div style="background:#cfcfcf;color:#1f1f1f;padding:6px 8px;font-weight:700;text-align:center;border-bottom:1px solid #8f8f8f;">Original</div>
                <div style="max-height:560px;overflow:auto;background:#efefef;">{left_html}</div>
            </div>
            <div style="min-width:0;">
                <div style="background:#cfcfcf;color:#1f1f1f;padding:6px 8px;font-weight:700;text-align:center;border-bottom:1px solid #8f8f8f;">Improved</div>
                <div style="max-height:560px;overflow:auto;background:#efefef;">{right_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <style>
    :root {
      --bg-primary: #0d0d0d;
      --bg-card: #16213e;
      --bg-sidebar: #0f0f1a;
      --accent-blue: #4fc3f7;
      --accent-red: #f44336;
      --accent-green: #4caf50;
      --text-primary: #ffffff;
      --text-muted: #a0a0b0;
      --border: #2a2a4a;
    }

    .stApp {
      background: var(--bg-primary);
      color: var(--text-primary);
    }

    section[data-testid="stSidebar"] {
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border);
    }

    .block-container {
            padding-top: 2.4rem;
      padding-bottom: 2rem;
      max-width: 1200px;
    }

    .logo-box {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      margin-bottom: 10px;
    }

    .logo-title {
      color: var(--accent-blue);
      font-size: 20px;
      font-weight: 700;
      margin: 0;
    }

    .logo-sub {
      color: var(--text-muted);
      font-size: 12px;
      margin: 2px 0 0 0;
    }

        div[role="radiogroup"] {
            background: rgba(79, 195, 247, 0.08);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 6px;
            gap: 8px;
            display: flex;
            flex-wrap: wrap;
            width: fit-content;
            margin-bottom: 6px;
        }

        div[role="radiogroup"] label {
            border: 1px solid transparent;
            border-radius: 999px;
            padding: 4px 12px;
            background: rgba(255, 255, 255, 0.03);
            transition: all 0.2s ease;
            min-height: 36px;
            display: inline-flex !important;
            align-items: center;
        }

        div[role="radiogroup"] label:hover {
            border-color: rgba(79, 195, 247, 0.45);
            background: rgba(79, 195, 247, 0.15);
        }

        div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
            border-color: rgba(14, 165, 233, 0.9);
            box-shadow: 0 4px 18px rgba(14, 165, 233, 0.35);
        }

        div[role="radiogroup"] label:has(input:checked) span {
            color: #03131d !important;
            font-weight: 700 !important;
        }

    div[data-testid="stMetricValue"] {
      color: var(--accent-green);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    """
    <div class="logo-box">
      <p class="logo-title">&lt;/&gt; AI Code Reviewer</p>
      <p class="logo-sub">Elevate Your Code Quality</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.divider()
language_options = supported_languages()
current_language = normalize_language(st.session_state.get("language", "Python"))
language_choice = st.sidebar.selectbox(
    "Source Language",
    language_options,
    index=language_options.index(current_language),
)
st.session_state["language"] = normalize_language(language_choice)

st.sidebar.multiselect(
    "Focus Areas",
    ["Security", "Performance", "Best Practices", "Code Style", "Documentation"],
)

render_top_nav()

if st.session_state["page"] == "💻 Code Editor":
    st.title("Intelligent Code Analysis")
    st.caption("Automated code review, security auditing, and optimization recommendations.")

    st.subheader("💻 Source Code Input")
    code_input = st.text_area(
        "Source Code",
        value=st.session_state.get("code_input", ""),
        placeholder=f"Paste your {st.session_state.get('language', 'Python')} code here...",
        height=400,
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔍 Analyze Code", type="primary", use_container_width=True):
            if code_input.strip():
                with st.spinner("Analyzing your code..."):
                    result = analyze_code_pipeline(
                        code_input, st.session_state.get("language", "Python")
                    )
                    st.session_state["result"] = result
                    st.session_state["code_input"] = code_input
                    st.session_state["history"].append(
                        {
                            "code": code_input[:100] + "...",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "language": st.session_state.get("language", "Python"),
                            "grade": result.get("quality_grade", "N/A"),
                            "issues": result.get("issues_count", 0),
                        }
                    )
                    st.session_state["page"] = "📊 Analysis Report"
                    st.rerun()
            else:
                st.warning("Please paste some code first.")
    with col2:
        st.empty()

if st.session_state["page"] == "📊 Analysis Report":
    result = st.session_state.get("result", {})

    if not result:
        st.info("No analysis yet. Go to Code Editor and analyze code first.")
    else:
        st.title("Analysis Report")

        if result.get("ai_fallback", False):
            st.warning(
                "AI response format was invalid, so fallback output was used for this run."
            )

        col1, col2, col3 = st.columns(3)
        col1.metric("QUALITY GRADE", result.get("quality_grade", "N/A"))
        col2.metric("ISSUES FOUND", result.get("issues_count", 0))
        col3.metric("REVIEWER", "AI (Grok)")

        bcol1, bcol2 = st.columns([1, 5])
        with bcol1:
            if st.button("🔄 Regenerate"):
                with st.spinner("Re-analyzing..."):
                    new_result = analyze_code_pipeline(
                        st.session_state.get("code_input", ""),
                        st.session_state.get("language", "Python"),
                    )
                    st.session_state["result"] = new_result
                    st.rerun()

        with bcol2:
            md_report = _build_markdown_report(result)
            pdf_report = _build_pdf_report_bytes(md_report)
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                st.download_button(
                    "📥 Download Report (MD)",
                    md_report,
                    "review_report.md",
                    "text/markdown",
                    key="download_report_md",
                )
            with dcol2:
                st.download_button(
                    "📄 Download Report (PDF)",
                    pdf_report,
                    "review_report.pdf",
                    "application/pdf",
                    key="download_report_pdf",
                )

        with st.expander("📊 Compare Changes (Diff View)", expanded=True):
            st.subheader("Side-by-Side Comparison")
            render_side_by_side_diff(
                result.get("original_code", ""), result.get("improved_code", "")
            )

        with st.expander("🔍 Static Analysis Findings"):
            static = result.get("static_analysis", {})
            unused_imports = static.get("unused_imports", [])
            if unused_imports:
                st.markdown("**Unused Imports:**")
                for imp in unused_imports:
                    st.markdown(
                        f"- `{imp['name']}` (from {imp['module']}) - line {imp['line']}"
                    )

            unused_funcs = static.get("unused_functions", [])
            if unused_funcs:
                st.markdown("**Unused Functions:**")
                for fn in unused_funcs:
                    st.markdown(f"- `{fn['name']}` - line {fn['line']}")

            unused_vars = static.get("unused_variables", [])
            if unused_vars:
                st.markdown("**Unused Variables:**")
                for var in unused_vars:
                    st.markdown(f"- `{var['name']}` - line {var['line']}")

            style_violations = static.get("style_violations", [])
            if style_violations:
                st.markdown("**Style Violations:**")
                for item in style_violations:
                    st.markdown(
                        f"- `{item['code']}` {item['message']} (line {item['line']}, col {item['column']})"
                    )

            external_tool_status = static.get("external_linter_tool_status", [])
            if external_tool_status:
                st.markdown("**External Linter Tool Status:**")
                for tool in external_tool_status:
                    state = "available" if tool.get("available") else "not available"
                    note = f" | {tool.get('note')}" if tool.get("note") else ""
                    st.markdown(
                        f"- `{tool.get('tool', 'tool')}`: {state} | issues: {tool.get('issues', 0)}{note}"
                    )

            external_violations = static.get("external_linter_violations", [])
            if external_violations:
                st.markdown("**External Linter Findings:**")
                for item in external_violations:
                    st.markdown(
                        f"- `{item.get('tool', 'linter')}` `{item.get('code', 'LINT')}` {item.get('message', 'Issue')} "
                        f"(line {item.get('line', '?')}, col {item.get('column', '?')})"
                    )

        with st.expander("🤖 Deep Code Review", expanded=True):
            st.subheader("Analysis Summary")
            st.write(result.get("analysis_summary", ""))

            st.subheader("Original Code")
            st.code(
                result.get("original_code", ""),
                language=str(result.get("language", st.session_state.get("language", "Python"))).lower(),
            )

            st.subheader("Issues Found")
            for issue in result.get("issues_found", []):
                st.markdown(f"- {issue}")

            st.subheader("Improved Code")
            st.code(
                result.get("improved_code", ""),
                language=str(result.get("language", st.session_state.get("language", "Python"))).lower(),
            )

            st.subheader("Detailed Explanations")
            explanations = result.get("detailed_explanations", {})

            st.markdown("#### 🚀 Scalability Impact")
            st.write(explanations.get("scalability_impact", ""))

            st.markdown("#### ⏱ Time/Space Complexity")
            st.write(explanations.get("time_space_complexity", ""))

            st.markdown("#### 🔒 Security Vulnerabilities")
            st.write(explanations.get("security_vulnerabilities", ""))

            st.markdown("#### ✅ Best Practices")
            st.write(explanations.get("best_practices", ""))

if st.session_state["page"] == "🤖 AI Assistant":
    st.title("🤖 AI Assistant")
    st.caption("Ask questions about your code review")

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_prompt = st.chat_input("Ask about your code...")
    if user_prompt:
        st.session_state["chat_messages"].append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                code_context = str(st.session_state.get("result", "No code analyzed yet"))
                response = ask_ai_assistant(
                    user_prompt,
                    code_context,
                    st.session_state["chat_messages"][:-1],
                )
                st.write(response)
        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": response}
        )

if st.session_state["page"] == "📜 History":
    st.title("📜 Review History")
    history = st.session_state.get("history", [])
    if not history:
        st.info("No reviews yet.")
    else:
        if st.button("🗑 Clear History"):
            st.session_state["history"] = []
            st.rerun()
        for i, entry in enumerate(reversed(history)):
            with st.expander(
                f"Review #{len(history)-i} - {entry['timestamp']} | {entry.get('language', 'Python')} | Grade: {entry['grade']} | Issues: {entry['issues']}"
            ):
                st.code(entry["code"], language=str(entry.get("language", "python")).lower())

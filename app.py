from datetime import datetime
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_suggestor import ask_ai_assistant
from code_analyzer import analyze_code_pipeline

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
      padding-top: 1.2rem;
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

page = st.sidebar.radio(
    "Navigation",
    ["💻 Code Editor", "📊 Analysis Report", "🤖 AI Assistant", "📜 History"],
    index=["💻 Code Editor", "📊 Analysis Report", "🤖 AI Assistant", "📜 History"].index(
        st.session_state.get("page", "💻 Code Editor")
    ),
)
st.session_state["page"] = page

st.sidebar.divider()
st.sidebar.write("Source Language: Python")
st.session_state["language"] = "Python"

st.sidebar.multiselect(
    "Focus Areas",
    ["Security", "Performance", "Best Practices", "Code Style", "Documentation"],
)

if st.session_state["page"] == "💻 Code Editor":
    st.title("Intelligent Code Analysis")
    st.caption("Automated code review, security auditing, and optimization recommendations.")

    st.subheader("💻 Source Code Input")
    code_input = st.text_area(
        "Source Code",
        value=st.session_state.get("code_input", ""),
        placeholder="Paste your Python code here...",
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
            md_report = f"""# Code Review Report
**Quality Grade:** {result.get('quality_grade','N/A')}
**Issues Found:** {result.get('issues_count',0)}

## Analysis Summary
{result.get('analysis_summary','')}

## Issues Found
{chr(10).join(['- ' + i for i in result.get('issues_found',[])])}

## Improved Code
```python
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
            st.download_button(
                "📥 Download Report (MD)", md_report, "review_report.md", "text/markdown"
            )

        with st.expander("📊 Compare Changes (Diff View)", expanded=True):
            st.subheader("Side-by-Side Comparison")
            orig_lines = result.get("original_code", "").splitlines()
            impr_lines = result.get("improved_code", "").splitlines()

            diff_col1, diff_col2 = st.columns(2)
            with diff_col1:
                st.markdown("**Original**")
                for i, line in enumerate(orig_lines):
                    st.markdown(
                        f'<div style="font-family:monospace;font-size:13px;background:#ff000015;padding:2px 8px">'
                        f'<span style="color:#555">{i+1}</span> '
                        f'<span style="color:#ff6b6b">{line}</span></div>',
                        unsafe_allow_html=True,
                    )
            with diff_col2:
                st.markdown("**Improved**")
                for i, line in enumerate(impr_lines):
                    st.markdown(
                        f'<div style="font-family:monospace;font-size:13px;background:#00ff0015;padding:2px 8px">'
                        f'<span style="color:#555">{i+1}</span> '
                        f'<span style="color:#69f0ae">{line}</span></div>',
                        unsafe_allow_html=True,
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

        with st.expander("🤖 Deep Code Review", expanded=True):
            st.subheader("Analysis Summary")
            st.write(result.get("analysis_summary", ""))

            st.subheader("Original Code")
            st.code(result.get("original_code", ""), language="python")

            st.subheader("Issues Found")
            for issue in result.get("issues_found", []):
                st.markdown(f"- {issue}")

            st.subheader("Improved Code")
            st.code(result.get("improved_code", ""), language="python")

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
                f"Review #{len(history)-i} - {entry['timestamp']} | Grade: {entry['grade']} | Issues: {entry['issues']}"
            ):
                st.code(entry["code"], language="python")

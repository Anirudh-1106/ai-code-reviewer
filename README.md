AI Code Reviewer: Smart Static Analysis + AI-Powered Suggestions
---
An AI-powered code review application that combines static analysis with LLM suggestions to help improve Python code quality.

This project includes:
- A Streamlit app for interactive code review and report export
- A Reflex app variant for full-stack style UI/state management
- Static analysis for unused imports, variables, functions, undefined names, and PEP 8 issues
- AI-assisted explanations, refactoring suggestions, and assistant chat

---

## Features

- Code quality scoring with issue count
- Static checks:
  - Unused imports
  - Unused variables
  - Unused functions
  - Undefined variable detection
  - PEP 8 style violations
- AI review:
  - Summary and detailed explanations
  - Suggested improved code
  - Consolidated issue list (static + AI)
- Visual diff (original vs improved code)
- Report generation:
  - Markdown report content
  - PDF download support
- Review history tracking
- Built-in AI assistant chat with current analysis context
- Demo code loader for quick testing

---

## Tech Stack

- Python
- Streamlit
- Reflex
- LangChain ecosystem:
  - langchain
  - langchain-core
  - langchain-community
  - langchain-groq
- anthropic
- python-dotenv
- pycodestyle
- reportlab

---

## Project Structure

    .
    ├── app.py                       # Streamlit app entry point
    ├── ai_suggestor.py              # AI integration and assistant helpers
    ├── code_analyzer.py             # Main analysis pipeline
    ├── code_parser.py               # Syntax parsing helpers
    ├── code_visitor.py              # Variable context tracking
    ├── error_detector.py            # Unused code checks
    ├── style_analyzer.py            # PEP 8 analyzer
    ├── full_stack_using_reflex/
    │   ├── full_stack_using_reflex.py
    │   └── state.py                 # Reflex state and actions
    ├── pages/                       # Reflex pages
    ├── components/                  # Shared UI components
    ├── assets/
    ├── requirements.txt
    └── rxconfig.py

---

## Installation

1. Clone the repository

       git clone https://github.com/your-username/ai_code_reviewer.git
       cd ai_code_reviewer

2. Create and activate a virtual environment

   Windows PowerShell:

       python -m venv venv
       Activate.ps1

   macOS/Linux:

       python3 -m venv venv
       source venv/bin/activate

3. Install dependencies

       pip install -r requirements.txt

4. Create a .env file for API keys (example)

       GROQ_API_KEY=your_groq_key
       ANTHROPIC_API_KEY=your_anthropic_key

Note:
Use whichever provider keys your ai_suggestor.py implementation expects.

---

## Run the App

### Streamlit version

    streamlit run app.py

Then open the local URL shown in the terminal.

### Reflex version

    reflex run

If needed, initialize Reflex once before first run:

    reflex init

---

## How It Works

1. User pastes Python code.
2. The parser validates syntax.
3. Static analysis modules detect structural/style issues.
4. AI review generates explanations and improved code suggestions.
5. Results are merged into a unified report with issue summary, grade, and diff.
6. User can export a PDF report and ask follow-up questions in assistant chat.

---

## Example Use Cases

- Quick code quality checks before commits
- Educational feedback for learners
- Refactoring guidance for messy scripts
- Generating review reports for submissions

---

## Roadmap

- Multi-language support beyond Python
- Unit test generation suggestions
- Security-focused rule packs
- Persistent database-backed review history
- Team collaboration and shared reports

---

## Troubleshooting

- If Streamlit fails to start, verify your virtual environment is active.
- If AI responses fail, check API keys in .env and provider quota.
- If Reflex command fails, ensure reflex is installed and compatible with your Python version.
- If no improvement is shown, the AI fallback may keep original code when output is invalid.

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request with a clear description

---

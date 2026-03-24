import reflex as rx

from components.navbar import navbar


def about() -> rx.Component:
    return rx.box(
        rx.container(
            rx.vstack(
                navbar(),
                rx.box(
                    rx.vstack(
                        rx.badge("PROJECT OVERVIEW", color_scheme="cyan", variant="soft"),
                        rx.heading("About AI Code Reviewer", size="8", color="#f8fafc"),
                        rx.text(
                            "AI Code Reviewer is a Reflex-powered platform for automated code quality analysis. "
                            "It combines AST-based static analysis with AI-generated suggestions so students "
                            "and instructors can review code faster with clear, actionable feedback.",
                            color="#cbd5e1",
                            font_size="1.08rem",
                            line_height="1.65",
                        ),
                        spacing="4",
                        align="start",
                        width="100%",
                    ),
                    width="100%",
                    max_width="1100px",
                    margin="0 auto",
                    border="1px solid #1f365d",
                    border_radius="18px",
                    background="linear-gradient(150deg, rgba(20, 32, 58, 0.72) 0%, rgba(7, 16, 36, 0.86) 60%)",
                    padding={"base": "1rem", "md": "1.25rem"},
                ),
                rx.grid(
                    rx.box(
                        rx.heading("What This App Does", size="5", margin_bottom="0.7rem"),
                        rx.vstack(
                            rx.text("- Parses Python code using AST and checks syntax health."),
                            rx.text("- Detects unused imports, functions, variables, and variable context."),
                            rx.text("- Uses AI to summarize quality issues and generate improved code."),
                            rx.text("- Shows side-by-side comparison between original and improved versions."),
                            rx.text("- Stores interactive review history with expandable full details."),
                            spacing="2",
                            align="start",
                            color="#cbd5e1",
                        ),
                        width="100%",
                        border="1px solid #334155",
                        border_radius="14px",
                        background="#0b1220",
                        padding="1rem",
                    ),
                    rx.box(
                        rx.heading("Analysis Pipeline", size="5", margin_bottom="0.7rem"),
                        rx.vstack(
                            rx.text("1. User submits code from Review Code page."),
                            rx.text("2. Parser validates syntax and catches parse errors."),
                            rx.text("3. Static analyzer detects unused symbols and variable context."),
                            rx.text("4. AI layer generates a code-quality summary and improved code."),
                            rx.text("5. Results are rendered as metrics, issues, and comparisons."),
                            spacing="2",
                            align="start",
                            color="#cbd5e1",
                        ),
                        width="100%",
                        border="1px solid #334155",
                        border_radius="14px",
                        background="#0b1220",
                        padding="1rem",
                    ),
                    columns={"base": "1", "md": "2"},
                    spacing="4",
                    width="100%",
                ),
                rx.box(
                    rx.heading("Technology Stack", size="5", margin_bottom="0.7rem"),
                    rx.text(
                        "Frontend: Reflex\n"
                        "Backend Logic: Python modules (code_parser, error_detector, code_visitor, code_analyzer)\n"
                        "AI Integration: ai_suggestor with LLM provider routing\n"
                        "Outputs: quality grade, issue list, improved code, static findings, and assistant chat",
                        color="#cbd5e1",
                        white_space="pre-wrap",
                        line_height="1.65",
                    ),
                    width="100%",
                    border="1px solid #334155",
                    border_radius="14px",
                    background="#0b1220",
                    padding="1rem",
                ),
                spacing="5",
                align="start",
                width="100%",
            ),
            max_width="1160px",
            width="100%",
            padding_y="1.6rem",
            padding_x={"base": "1rem", "md": "1.3rem"},
        ),
        width="100%",
        display="flex",
        justify_content="center",
    )

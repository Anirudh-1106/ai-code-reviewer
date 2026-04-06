import reflex as rx

from components.navbar import navbar
from components.premium import metric_tile, premium_panel, staggered_panel
from full_stack_using_reflex.state import ReviewerState


def _severity_chip(item: dict[str, str]) -> rx.Component:
    return rx.box(
        rx.text(item["severity"], font_weight="700", color=item["fg"], font_size="0.8rem"),
        rx.badge(item["count"], color_scheme="gray", variant="soft", radius="full"),
        display="flex",
        align_items="center",
        gap="0.5rem",
        padding="0.35rem 0.68rem",
        border_radius="999px",
        background=item["bg"],
        border=item["border"],
        box_shadow="inset 0 0 0 1px rgba(255, 255, 255, 0.04)",
    )


def _grouped_issue_block(title: str, items: rx.Var) -> rx.Component:
    return premium_panel(
        rx.text(title, color="#f0f6ff", font_weight="700", margin_bottom="0.55rem"),
        rx.vstack(
            rx.foreach(
                items,
                lambda issue: rx.hstack(
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="999px",
                        background="linear-gradient(160deg, #7dd3fc 0%, #fbbf24 100%)",
                        margin_top="0.45rem",
                    ),
                    rx.text(issue, color="#dbe7fa", width="100%", line_height="1.45"),
                    width="100%",
                    align="start",
                    spacing="3",
                ),
            ),
            width="100%",
            spacing="2",
            align="start",
        ),
    )


def posts() -> rx.Component:
    return rx.box(
        rx.container(
            rx.vstack(
                navbar(),
                rx.vstack(
            rx.heading("Review Code", size="7", color="#f8fafc", margin_top="0.75rem"),
            rx.text(
                "Paste code in any supported language and run static checks, external tool diagnostics, and AI-assisted improvements.",
                color="#c4d5ee",
            ),
            rx.hstack(
                rx.text("Language", color="#93c5fd", font_weight="600"),
                rx.select(
                    ReviewerState.available_languages,
                    value=ReviewerState.selected_language,
                    on_change=ReviewerState.update_language,
                    width="220px",
                    color="#f1f6ff",
                    background="rgba(8, 17, 35, 0.78)",
                    border="1px solid rgba(151, 183, 227, 0.34)",
                    border_radius="12px",
                ),
                spacing="3",
                align="center",
            ),
            rx.text_area(
                value=ReviewerState.code_input,
                on_change=ReviewerState.update_code_input,
                placeholder="Paste your source code here...",
                min_height="280px",
                width="100%",
                background="rgba(8, 18, 36, 0.82)",
                border="1px solid rgba(158, 189, 230, 0.26)",
                border_radius="14px",
                color="#e8f0fd",
                box_shadow="inset 0 0 0 1px rgba(12, 28, 55, 0.58)",
            ),
            rx.hstack(
                rx.button(
                    "Analyze Code",
                    on_click=ReviewerState.analyze,
                    color_scheme="orange",
                    border_radius="11px",
                    box_shadow="0 8px 18px rgba(244, 171, 72, 0.32)",
                    _hover={"transform": "translateY(-2px) scale(1.01)"},
                ),
                rx.button(
                    "Load Demo",
                    on_click=ReviewerState.load_demo,
                    variant="outline",
                    color_scheme="orange",
                    border_radius="11px",
                ),
                rx.button(
                    "Download PDF Report",
                    on_click=ReviewerState.download_pdf_report,
                    variant="outline",
                    color_scheme="orange",
                    border_radius="11px",
                ),
                spacing="3",
            ),
            rx.cond(
                ReviewerState.error_message != "",
                rx.box(
                    rx.text(ReviewerState.error_message, color="#fecaca"),
                    width="100%",
                    border="1px solid #7f1d1d",
                    background="rgba(93, 12, 23, 0.55)",
                    border_radius="10px",
                    padding="0.7rem",
                ),
            ),
            rx.grid(
                metric_tile("Quality Grade", ReviewerState.quality_grade, accent="#f59e0b"),
                metric_tile("Issues Found", ReviewerState.issues_count.to_string(), accent="#60a5fa"),
                columns={"base": "1", "md": "2"},
                spacing="4",
                width="100%",
            ),
            rx.cond(
                ReviewerState.severity_breakdown.length() > 0,
                staggered_panel(
                    rx.text("Severity Breakdown", color="#f8fafc", font_weight="700", margin_bottom="0.6rem"),
                    rx.hstack(
                        rx.foreach(ReviewerState.severity_breakdown, _severity_chip),
                        spacing="2",
                        flex_wrap="wrap",
                        width="100%",
                    ),
                    step=0,
                ),
            ),
            rx.cond(
                ReviewerState.ai_fallback,
                rx.text(
                    "AI response fallback was used for this run.",
                    color="#facc15",
                    font_size="0.95rem",
                ),
            ),
            staggered_panel(
                rx.heading("Analysis Summary", size="5", margin_bottom="0.5rem"),
                rx.text(ReviewerState.analysis_summary, color="#cbd5e1", white_space="pre-wrap"),
                step=1,
            ),
            staggered_panel(
                rx.heading("Side-by-Side Comparison", size="5", margin_bottom="0.75rem"),
                rx.grid(
                    rx.box(
                        rx.text("Original", color="#cbd5e1", font_weight="700", margin_bottom="0.5rem"),
                        rx.text(
                            ReviewerState.original_code_with_lines,
                            white_space="pre-wrap",
                            font_family="Consolas, monospace",
                            font_size="0.9rem",
                            color="#fecaca",
                        ),
                        width="100%",
                        min_height="240px",
                        max_height="360px",
                        overflow="auto",
                        border="1px solid #3f3f46",
                        border_radius="10px",
                        background="#111827",
                        padding="0.75rem",
                    ),
                    rx.box(
                        rx.text("Improved", color="#cbd5e1", font_weight="700", margin_bottom="0.5rem"),
                        rx.text(
                            ReviewerState.improved_code_with_lines,
                            white_space="pre-wrap",
                            font_family="Consolas, monospace",
                            font_size="0.9rem",
                            color="#bbf7d0",
                        ),
                        width="100%",
                        min_height="240px",
                        max_height="360px",
                        overflow="auto",
                        border="1px solid #3f3f46",
                        border_radius="10px",
                        background="#111827",
                        padding="0.75rem",
                    ),
                    columns={"base": "1", "lg": "2"},
                    width="100%",
                    spacing="4",
                    align_items="start",
                ),
                step=2,
            ),
            staggered_panel(
                rx.heading("Issues Found", size="5", margin_bottom="0.5rem"),
                rx.vstack(
                    rx.cond(
                        ReviewerState.grouped_external_issues.length() > 0,
                        _grouped_issue_block("External Tool Findings", ReviewerState.grouped_external_issues),
                    ),
                    rx.cond(
                        ReviewerState.grouped_static_issues.length() > 0,
                        _grouped_issue_block("Static Analysis Findings", ReviewerState.grouped_static_issues),
                    ),
                    rx.cond(
                        ReviewerState.grouped_ai_issues.length() > 0,
                        _grouped_issue_block("AI Review Findings", ReviewerState.grouped_ai_issues),
                    ),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                step=3,
            ),
            staggered_panel(
                rx.heading("Improved Code", size="5", margin_bottom="0.5rem"),
                rx.text(
                    ReviewerState.improved_code,
                    white_space="pre-wrap",
                    font_family="Consolas, monospace",
                    color="#bae6fd",
                ),
                step=4,
            ),
            staggered_panel(
                rx.heading("Static Analysis", size="5", margin_bottom="0.5rem"),
                rx.text("Unused Imports", color="#93c5fd", font_weight="600"),
                rx.foreach(
                    ReviewerState.unused_imports,
                    lambda item: rx.text(item, color="#e2e8f0", width="100%"),
                ),
                rx.text("Unused Functions", color="#93c5fd", font_weight="600", margin_top="0.75rem"),
                rx.foreach(
                    ReviewerState.unused_functions,
                    lambda item: rx.text(item, color="#e2e8f0", width="100%"),
                ),
                rx.text("Unused Variables", color="#93c5fd", font_weight="600", margin_top="0.75rem"),
                rx.foreach(
                    ReviewerState.unused_variables,
                    lambda item: rx.text(item, color="#e2e8f0", width="100%"),
                ),
                rx.text("Style Violations", color="#93c5fd", font_weight="600", margin_top="0.75rem"),
                rx.foreach(
                    ReviewerState.style_violations,
                    lambda item: rx.text(item, color="#e2e8f0", width="100%"),
                ),
                rx.text("External Linter Tool Status", color="#93c5fd", font_weight="600", margin_top="0.75rem"),
                rx.foreach(
                    ReviewerState.external_linter_tool_status,
                    lambda item: rx.text(item, color="#e2e8f0", width="100%"),
                ),
                rx.text("External Linter Findings", color="#93c5fd", font_weight="600", margin_top="0.75rem"),
                rx.foreach(
                    ReviewerState.external_linter_violations,
                    lambda item: rx.text(item, color="#e2e8f0", width="100%"),
                ),
                step=5,
            ),
            staggered_panel(
                rx.heading("Variable Context (code_visitor)", size="5", margin_bottom="0.5rem"),
                rx.text("Created Variables", color="#93c5fd", font_weight="600"),
                rx.foreach(
                    ReviewerState.created_variables,
                    lambda item: rx.text(item, color="#e2e8f0", width="100%"),
                ),
                rx.text("Used Variables", color="#93c5fd", font_weight="600", margin_top="0.75rem"),
                rx.foreach(
                    ReviewerState.used_variables,
                    lambda item: rx.text(item, color="#e2e8f0", width="100%"),
                ),
                step=6,
            ),
            spacing="4",
            align="start",
            width="100%",
                ),
                width="100%",
                max_width="1100px",
                margin="0 auto",
                spacing="4",
                align="start",
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

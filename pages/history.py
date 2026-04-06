import reflex as rx

from components.navbar import navbar
from components.premium import staggered_panel
from full_stack_using_reflex.state import ReviewerState


def history() -> rx.Component:
    return rx.box(
        rx.container(
            rx.vstack(
                navbar(),
                rx.vstack(
            rx.hstack(
                rx.heading("Review History", size="7", color="#f8fafc", margin_top="0.75rem"),
                rx.spacer(),
                rx.button(
                    "Clear History",
                    on_click=ReviewerState.clear_history,
                    variant="outline",
                    color_scheme="orange",
                    border_radius="10px",
                ),
                width="100%",
            ),
            rx.cond(
                ReviewerState.history_entries.length() == 0,
                staggered_panel(
                    rx.text("No reviews yet. Analyze code from the Review Code page."),
                    border_radius="14px",
                    padding="1rem",
                    step=1,
                ),
                rx.vstack(
                    rx.foreach(
                        ReviewerState.history_entries,
                        lambda entry: staggered_panel(
                            rx.hstack(
                                rx.text(entry["summary"], color="#cbd5e1", width="100%"),
                                rx.button(
                                    rx.cond(
                                        ReviewerState.selected_history_id == entry["id"],
                                        "Hide",
                                        "View",
                                    ),
                                    on_click=ReviewerState.toggle_history_entry(entry["id"]),
                                    size="1",
                                    variant="outline",
                                    color_scheme="orange",
                                    border_radius="10px",
                                ),
                                width="100%",
                                align="center",
                                spacing="3",
                            ),
                            rx.cond(
                                ReviewerState.selected_history_id == entry["id"],
                                rx.box(
                                    rx.text(
                                        f"Timestamp: {entry['timestamp']} | Language: {entry.get('language', 'Python')} | Grade: {entry['grade']} | Issues: {entry['issues_count']}",
                                        color="#93c5fd",
                                        margin_top="0.8rem",
                                    ),
                                    rx.text("Analysis Summary", color="#cbd5e1", font_weight="700", margin_top="0.8rem"),
                                    rx.text(entry["analysis_summary"], color="#e2e8f0", white_space="pre-wrap"),
                                    rx.text("Issues Found", color="#cbd5e1", font_weight="700", margin_top="0.8rem"),
                                    rx.text(entry["issues_found"], color="#f8fafc", white_space="pre-wrap"),
                                    rx.text("Original Code", color="#cbd5e1", font_weight="700", margin_top="0.8rem"),
                                    rx.text(
                                        entry["original_code"],
                                        color="#fecaca",
                                        white_space="pre-wrap",
                                        font_family="Consolas, monospace",
                                    ),
                                    rx.text("Improved Code", color="#cbd5e1", font_weight="700", margin_top="0.8rem"),
                                    rx.text(
                                        entry["improved_code"],
                                        color="#bbf7d0",
                                        white_space="pre-wrap",
                                        font_family="Consolas, monospace",
                                    ),
                                    width="100%",
                                ),
                            ),
                            border_radius="14px",
                            padding="0.9rem",
                            step=2,
                        ),
                    ),
                    width="100%",
                    spacing="3",
                ),
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

import reflex as rx

from components.navbar import navbar
from components.premium import staggered_panel
from full_stack_using_reflex.state import ReviewerState


def _chat_bubble(message: dict[str, str]) -> rx.Component:
    is_user = message["role"] == "user"
    return rx.hstack(
        rx.cond(
            is_user,
            rx.fragment(),
            rx.box(
                rx.icon(tag="bot", size=16, color="#7dd3fc"),
                background="#0b2135",
                border="1px solid #164e63",
                border_radius="999px",
                width="30px",
                height="30px",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
                margin_top="2px",
            ),
        ),
        rx.box(
            rx.text(
                rx.cond(is_user, "You", "AI Assistant"),
                color=rx.cond(is_user, "#bfdbfe", "#7dd3fc"),
                font_size="0.78rem",
                font_weight="700",
                margin_bottom="0.35rem",
                text_transform="uppercase",
                letter_spacing="0.06em",
            ),
            rx.text(
                message["content"],
                color="#f8fafc",
                white_space="pre-wrap",
                line_height="1.55",
            ),
            background=rx.cond(
                is_user,
                "linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)",
                "#111827",
            ),
            border=rx.cond(
                is_user,
                "1px solid #0284c7",
                "1px solid #334155",
            ),
            border_radius="14px",
            padding="0.75rem 0.9rem",
            max_width={"base": "100%", "md": "82%"},
            width="fit-content",
            box_shadow="0 8px 24px rgba(2, 6, 23, 0.35)",
        ),
        rx.cond(
            is_user,
            rx.box(
                rx.icon(tag="user", size=16, color="#bfdbfe"),
                background="#082f49",
                border="1px solid #0369a1",
                border_radius="999px",
                width="30px",
                height="30px",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
                margin_top="2px",
            ),
            rx.fragment(),
        ),
        justify=rx.cond(is_user, "end", "start"),
        align="start",
        width="100%",
        spacing="3",
    )


def assistant() -> rx.Component:
    return rx.box(
        rx.container(
            rx.vstack(
                navbar(),
                staggered_panel(
                    rx.hstack(
                        rx.heading("AI Assistant", size="7", color="#f8fafc"),
                        rx.spacer(),
                        rx.button(
                            "Clear Chat",
                            on_click=ReviewerState.clear_assistant_chat,
                            variant="outline",
                            color_scheme="orange",
                            size="1",
                            border_radius="10px",
                        ),
                        width="100%",
                    ),
                    rx.heading("Ask the AI Assistant", size="8", color="#f8fafc"),
                    rx.text(
                        "Ask follow-up questions on your analysis, suggested fixes, security, or optimizations.",
                        color="#c2d4ee",
                        font_size="1.05rem",
                    ),
                    rx.cond(
                        ReviewerState.assistant_messages.length() == 0,
                        rx.vstack(
                            rx.icon(tag="messages-square", size=26, color="#38bdf8"),
                            rx.text(
                                "No messages yet. Ask your first question about the analyzed code.",
                                color="#94a3b8",
                            ),
                            background="rgba(7, 18, 36, 0.66)",
                            border="1px solid rgba(149, 182, 225, 0.24)",
                            border_radius="14px",
                            align="center",
                            justify="center",
                            width="100%",
                            height="240px",
                            spacing="3",
                        ),
                        rx.vstack(
                            rx.foreach(
                                ReviewerState.assistant_messages,
                                _chat_bubble,
                            ),
                            width="100%",
                            min_height="220px",
                            max_height="520px",
                            overflow_y="auto",
                            spacing="3",
                            align="start",
                            padding_y="0.4rem",
                            background="rgba(6, 15, 33, 0.56)",
                            border="1px solid rgba(149, 182, 225, 0.24)",
                            border_radius="14px",
                            padding_x="0.75rem",
                        ),
                    ),
                    rx.divider(border_color="rgba(149, 182, 225, 0.24)", width="100%"),
                    rx.text_area(
                        value=ReviewerState.assistant_prompt,
                        on_change=ReviewerState.update_assistant_prompt,
                        placeholder="Ask anything about your code review...",
                        width="100%",
                        min_height="90px",
                        max_height="180px",
                        background="rgba(8, 18, 36, 0.82)",
                        color="#f8fafc",
                        border="1px solid rgba(151, 181, 223, 0.3)",
                        border_radius="14px",
                    ),
                    rx.hstack(
                        rx.text(
                            "Connected to your latest analysis context.",
                            color="#94a3b8",
                            font_size="0.88rem",
                        ),
                        rx.spacer(),
                        rx.button(
                            "Send",
                            on_click=ReviewerState.send_assistant_message,
                            color_scheme="orange",
                            size="2",
                            min_width="90px",
                            border_radius="11px",
                            box_shadow="0 8px 18px rgba(244, 171, 72, 0.32)",
                        ),
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                    align="start",
                    max_width="1000px",
                    margin="0 auto",
                    padding="1.15rem",
                    border_radius="18px",
                    step=0,
                ),
                width="100%",
                spacing="5",
                align="center",
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

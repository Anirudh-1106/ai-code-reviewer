import reflex as rx


def hero() -> rx.Component:
    return rx.box(
        rx.box(
            rx.grid(
                rx.vstack(
                    rx.badge(
                        "AI-POWERED CODE QUALITY",
                        color_scheme="cyan",
                        variant="soft",
                        radius="full",
                        font_size="0.72rem",
                        padding_x="0.65rem",
                        padding_y="0.2rem",
                    ),
                    rx.heading(
                        "Review Your Code with AI",
                        size="9",
                        color="#f8fafc",
                        line_height="1.05",
                        letter_spacing="-0.02em",
                    ),
                    rx.text(
                        "Detect bugs, improve readability, and get optimization suggestions with a student-friendly code review assistant.",
                        color="#cbd5e1",
                        font_size="1.2rem",
                        max_width="560px",
                        line_height="1.55",
                    ),
                    rx.hstack(
                        rx.link(
                            rx.button(
                                "Start Reviewing",
                                color_scheme="sky",
                                variant="solid",
                                size="3",
                                _hover={"transform": "translateY(-2px)"},
                            ),
                            href="/posts",
                        ),
                        rx.link(
                            rx.button(
                                "Try Demo",
                                variant="outline",
                                color_scheme="sky",
                                size="3",
                                _hover={"background": "rgba(56, 189, 248, 0.08)"},
                            ),
                            href="/posts",
                        ),
                        spacing="4",
                    ),
                    align="start",
                    spacing="6",
                    width="100%",
                    justify="center",
                ),
                rx.box(
                    rx.image(
                        src="/code-review-hero.svg",
                        alt="Code review illustration",
                        width="100%",
                        max_width="520px",
                        border_radius="18px",
                        border="1px solid #334155",
                        box_shadow="0 18px 34px rgba(2, 6, 23, 0.45)",
                    ),
                    display="flex",
                    justify_content="center",
                    width="100%",
                ),
                columns={"base": "1", "lg": "2"},
                spacing="9",
                width="100%",
                align_items="center",
            ),
            padding={"base": "2.4rem", "md": "3.1rem", "lg": "3.8rem"},
        ),
        width="100%",
        border="1px solid #1f365d",
        border_radius="22px",
        background="linear-gradient(150deg, rgba(20, 32, 58, 0.72) 0%, rgba(7, 16, 36, 0.86) 60%)",
    )

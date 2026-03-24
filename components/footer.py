import reflex as rx


def footer() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.link("About", href="/about", color="#bae6fd", _hover={"color": "#7dd3fc"}),
            rx.link(
                "GitHub",
                href="https://github.com",
                color="#bae6fd",
                is_external=True,
                _hover={"color": "#7dd3fc"},
            ),
            rx.link("Contact", href="mailto:hello@example.com", color="#bae6fd", _hover={"color": "#7dd3fc"}),
            spacing="5",
            justify="center",
            width="100%",
        ),
        rx.text("Built with Reflex", color="#94a3b8", font_size="0.95rem"),
        rx.text("Copyright 2026 AI Code Reviewer", color="#64748b", font_size="0.9rem"),
        align="center",
        spacing="2",
        width="100%",
        border_top="1px solid #334155",
        padding_top="1.2rem",
        margin_top="1.5rem",
    )

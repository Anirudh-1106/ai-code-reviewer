import reflex as rx


def navbar() -> rx.Component:
    links = rx.hstack(
        rx.link(
            "Home",
            href="/",
            color="white",
            font_weight="500",
            _hover={"color": "#38bdf8", "text_decoration": "none"},
        ),
        rx.link(
            "Review Code",
            href="/posts",
            color="white",
            font_weight="500",
            _hover={"color": "#38bdf8", "text_decoration": "none"},
        ),
        rx.link(
            "AI Assistant",
            href="/assistant",
            color="white",
            font_weight="500",
            _hover={"color": "#38bdf8", "text_decoration": "none"},
        ),
        rx.link(
            "History",
            href="/history",
            color="white",
            font_weight="500",
            _hover={"color": "#38bdf8", "text_decoration": "none"},
        ),
        rx.link(
            "About",
            href="/about",
            color="white",
            font_weight="500",
            _hover={"color": "#38bdf8", "text_decoration": "none"},
        ),
        spacing="6",
        align="center",
    )

    brand = rx.hstack(
        rx.icon(tag="sparkles", size=20, color="#38bdf8"),
        rx.text("AI Code Reviewer", size="4", weight="bold", color="white"),
        spacing="2",
        align="center",
    )

    left_section = rx.hstack(
        rx.link(
            rx.image(
                src="/logo.svg",
                alt="AI Code Reviewer",
                width="32px",
                height="32px",
                border_radius="8px",
            ),
            href="/",
        ),
        brand,
        spacing="3",
        align="center",
        padding_right="1.5rem",
    )

    return rx.box(
        rx.flex(
            left_section,
            rx.spacer(),
            rx.box(links),
            align="center",
            width="100%",
            gap="6",
        ),
        background="linear-gradient(90deg, #0f172a 0%, #1e293b 100%)",
        border="1px solid #334155",
        border_radius="16px",
        padding="0.95rem 1.2rem",
        position="sticky",
        top="0.75rem",
        z_index="100",
        backdrop_filter="blur(6px)",
        box_shadow="0 10px 30px rgba(0, 0, 0, 0.25)",
        max_width="1100px",
        width="100%",
        margin="0 auto",
    )

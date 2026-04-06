import reflex as rx


def _nav_link(label: str, href: str) -> rx.Component:
    is_active = rx.State.router.page.path == href
    return rx.link(
        label,
        href=href,
        color=rx.cond(is_active, "#f9fbff", "#d7e5fb"),
        font_weight=rx.cond(is_active, "700", "600"),
        padding="0.38rem 0.78rem",
        border_radius="999px",
        background=rx.cond(is_active, "rgba(126, 199, 255, 0.2)", "transparent"),
        border=rx.cond(is_active, "1px solid rgba(143, 208, 255, 0.42)", "1px solid transparent"),
        _hover={
            "color": "#f5fbff",
            "text_decoration": "none",
            "background": "rgba(126, 199, 255, 0.14)",
        },
    )


def navbar() -> rx.Component:
    links = rx.hstack(
        _nav_link("Home", "/"),
        _nav_link("Review Code", "/posts"),
        _nav_link("AI Assistant", "/assistant"),
        _nav_link("History", "/history"),
        _nav_link("About", "/about"),
        spacing="2",
        align="center",
        background="rgba(3, 12, 28, 0.44)",
        border="1px solid rgba(129, 173, 230, 0.22)",
        border_radius="999px",
        padding="0.22rem",
    )

    brand = rx.hstack(
        rx.box(
            rx.icon(tag="sparkles", size=16, color="#06111f"),
            background="linear-gradient(145deg, #8fd7ff 0%, #3ea8ff 100%)",
            border_radius="10px",
            padding="0.42rem",
            box_shadow="0 8px 18px rgba(62, 168, 255, 0.45)",
        ),
        rx.vstack(
            rx.text("AI Code Reviewer", size="4", weight="bold", color="#f8fcff"),
            rx.text("Multi-Language Engineering Intelligence", color="#9fb4d3", font_size="0.7rem"),
            spacing="0",
            align="start",
        ),
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
                border="1px solid rgba(169, 205, 246, 0.38)",
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
        background="linear-gradient(115deg, rgba(7, 16, 34, 0.92) 0%, rgba(11, 22, 44, 0.86) 100%)",
        border="1px solid rgba(148, 184, 230, 0.28)",
        border_radius="18px",
        padding="0.95rem 1.2rem",
        position="sticky",
        top="0.75rem",
        z_index="100",
        backdrop_filter="blur(14px)",
        box_shadow="0 16px 42px rgba(0, 0, 0, 0.38)",
        max_width="1100px",
        width="100%",
        margin="0 auto",
    )

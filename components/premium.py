import reflex as rx


def premium_panel(*children, **overrides) -> rx.Component:
    style = {
        "width": "100%",
        "border": "none",
        "border_radius": "14px",
        "background": "linear-gradient(145deg, rgba(10, 21, 42, 0.86) 0%, rgba(8, 17, 36, 0.82) 100%)",
        "padding": "1rem",
        "backdrop_filter": "blur(8px)",
        "box_shadow": "inset 0 0 0 1px rgba(171, 200, 236, 0.14), 0 14px 30px rgba(2, 8, 24, 0.28)",
        "transition": "transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease",
        "_hover": {
            "transform": "translateY(-2px)",
            "box_shadow": "inset 0 0 0 1px rgba(171, 200, 236, 0.2), 0 18px 36px rgba(2, 8, 24, 0.34)",
        },
    }
    style.update(overrides)
    return rx.box(*children, **style)


def staggered_panel(*children, step: int = 0, **overrides) -> rx.Component:
    delay = 80 + (step * 70)
    return premium_panel(
        *children,
        animation="fadeIn 0.45s ease",
        animation_delay=f"{delay}ms",
        animation_fill_mode="both",
        **overrides,
    )


def status_chip(text: str, tone: str = "info") -> rx.Component:
    tones = {
        "info": {
            "fg": "#dbeafe",
            "bg": "rgba(30, 64, 175, 0.28)",
            "border": "1px solid rgba(96, 165, 250, 0.42)",
        },
        "success": {
            "fg": "#bbf7d0",
            "bg": "rgba(20, 83, 45, 0.32)",
            "border": "1px solid rgba(74, 222, 128, 0.42)",
        },
        "warning": {
            "fg": "#fde68a",
            "bg": "rgba(113, 63, 18, 0.35)",
            "border": "1px solid rgba(245, 158, 11, 0.44)",
        },
        "danger": {
            "fg": "#fecaca",
            "bg": "rgba(127, 29, 29, 0.42)",
            "border": "1px solid rgba(248, 113, 113, 0.52)",
        },
    }
    style = tones.get(tone, tones["info"])
    return rx.box(
        text,
        color=style["fg"],
        font_size="0.78rem",
        font_weight="700",
        letter_spacing="0.03em",
        padding="0.22rem 0.58rem",
        border_radius="999px",
        background=style["bg"],
        border=style["border"],
        width="fit-content",
        box_shadow="inset 0 0 0 1px rgba(255, 255, 255, 0.03)",
    )


def metric_tile(label: str, value, accent: str = "#93c5fd") -> rx.Component:
    return premium_panel(
        rx.text(label, color="#90a8c8", font_size="0.85rem", text_transform="uppercase", letter_spacing="0.06em"),
        rx.text(value, color="#f8fbff", font_size="1.8rem", font_weight="700", line_height="1.1"),
        border=f"1px solid {accent}33",
        background="linear-gradient(150deg, rgba(9, 20, 38, 0.9) 0%, rgba(7, 16, 32, 0.86) 100%)",
        padding="0.9rem 1rem",
    )

import reflex as rx

from components.hero import hero
from components.navbar import navbar


def index() -> rx.Component:
    return rx.box(
        rx.container(
            rx.vstack(
                navbar(),
                hero(),
                spacing="8",
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

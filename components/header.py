import reflex as rx


def header() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading("I am Simran!", size="7", color="#f8fafc"),
            rx.heading("This project is about intelligent code review.", size="5", color="#cbd5e1"),
            rx.button(
                "Click here!",
                color_scheme="cyan",
                _hover={"background": "#0891b2", "transform": "translateY(-2px)"},
            ),
            align="start",
            spacing="4",
            width="100%",
        ),
        rx.box(
            rx.image(
                src="/code-grid.svg",
                alt="Project preview",
                width="100%",
                max_width="380px",
                border_radius="16px",
                border="1px solid #334155",
            ),
            display="flex",
            justify_content="center",
            width="100%",
        ),
        columns={"base": "1", "md": "2", "lg": "3"},
        spacing="7",
        width="100%",
        align_items="center",
        padding="1rem 0",
    )

import reflex as rx

from pages.about import about
from pages.assistant import assistant
from pages.history import history
from pages.index import index
from pages.posts import posts

app = rx.App(
    style={
        "background": (
            "radial-gradient(circle at 8% 8%, rgba(46, 127, 228, 0.22) 0%, rgba(8, 16, 32, 0) 35%),"
            "radial-gradient(circle at 88% 12%, rgba(244, 171, 72, 0.14) 0%, rgba(8, 16, 32, 0) 36%),"
            "linear-gradient(160deg, #040811 0%, #061127 45%, #07162d 100%)"
        ),
        "min_height": "100vh",
        "color": "#e6edf7",
        "font_family": "'Sora', 'Manrope', 'Segoe UI', sans-serif",
        "letter_spacing": "-0.01em",
    }
)
app.add_page(index, route="/", title="AI Code Reviewer")
app.add_page(about, route="/about", title="About")
app.add_page(assistant, route="/assistant", title="AI Assistant")
app.add_page(posts, route="/posts", title="Review Code")
app.add_page(history, route="/history", title="History")

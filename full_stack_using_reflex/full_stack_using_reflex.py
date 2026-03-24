import reflex as rx

from pages.about import about
from pages.assistant import assistant
from pages.history import history
from pages.index import index
from pages.posts import posts

app = rx.App(
    style={
        "background": "radial-gradient(circle at 12% 14%, #13264a 0%, #030b1f 40%, #020617 75%)",
        "min_height": "100vh",
        "color": "#e2e8f0",
        "font_family": "'Segoe UI', sans-serif",
    }
)
app.add_page(index, route="/", title="AI Code Reviewer")
app.add_page(about, route="/about", title="About")
app.add_page(assistant, route="/assistant", title="AI Assistant")
app.add_page(posts, route="/posts", title="Review Code")
app.add_page(history, route="/history", title="History")

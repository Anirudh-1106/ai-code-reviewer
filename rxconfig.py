import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="full_stack_using_reflex",
    disable_plugins=[SitemapPlugin],
)

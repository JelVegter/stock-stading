from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash
from render.style import (
    template,
    font,
    font_color,
    CONTENT_STYLE,
    color_1,
    color_2,
    bar_color,
)

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR], use_pages=True)
app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    style=CONTENT_STYLE,
    children=[
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(
                    dbc.NavLink("Portfolio Analysis", href="/portfolio-analysis")
                ),
                dbc.NavItem(
                    dbc.NavLink("Efficient Frontier", href="/efficient-frontier")
                ),
            ],
            brand="Stock Trading App",
            links_left=True
            # brand_href="/portfolio-analysis",
            # color="dark",
            # dark=False,
        ),
        # html.Div(
        #     [
        #         html.Div(
        #             dcc.Link(
        #                 f"{page['name']} - {page['path']}", href=page["relative_path"]
        #             )
        #         )
        #         for page in dash.page_registry.values()
        #     ]
        # ),
        dash.page_container,
    ],
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)

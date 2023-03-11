# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, dash_table, register_page, callback
import plotly.express as px
from src.analysis.portfolio_analysis import PortfolioAnalysis
from src.analysis.stock_returns import fetch_stock_returns
from src.etl import get_available_symbols
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from pandas import DataFrame
from dash_bootstrap_templates import load_figure_template
from render.style import (
    template,
    font,
    font_color,
    CONTENT_STYLE,
    color_1,
    color_2,
    bar_color,
)

register_page(__name__)


def create_performance_graph(portfolio_analysis: PortfolioAnalysis):
    df = portfolio_analysis.benchmark_df.copy()
    portfolio_col = "Cumulative Returns Portfolio"
    benchmark_col = "Cumulative Returns S&P500"
    df = df.rename(
        columns={
            "Portfolio": portfolio_col,
            portfolio_analysis.benchmark_portfolio: benchmark_col,
        }
    )
    df.reset_index(inplace=True)
    fig = px.line(
        df,
        x="Date",
        y=[portfolio_col, benchmark_col],
        title="Portfolio vs Benchmark",
    )
    fig["layout"] = {
        "template": template,
        "yaxis": dict(
            showgrid=True,
            zeroline=False,
            showline=True,
            showticklabels=True,
        ),
        "xaxis": dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor="rgb(204, 204, 204)",
            linewidth=2,
            ticks="outside",
            tickfont=dict(
                family=font,
                size=12,
                color="rgb(82, 82, 82)",
            ),
        ),
        "autosize": True,
    }
    return fig


external_stylesheets = [
    "https://github.com/plotly/dash-app-stylesheets/blob/master/dash-goldman-sachs-report-js.js"
]
BS = "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css"


# app = Dash(__name__, external_stylesheets=[BS])
load_figure_template("ZEPHYR")

layout = html.Div(
    children=[
        html.H2(
            children="Portfolio Analysis",
            style={
                "padding-bottom": "1rem",
                "padding-top": "1rem",
                "padding-left": "0.5rem",
                "font-color": font_color,
                "vertical-align": "text-bottom",
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(children="Evaluate stock returns."),
                        dcc.Dropdown(
                            id="symbol-input",
                            options=get_available_symbols(),
                            multi=True,
                            style={
                                "width": "100%",
                                "margin-top": "1rem",
                            },
                        ),
                        html.Div(
                            id="mean-portfolio-returns",
                            style={
                                "margin-top": "2rem",
                                "margin-bottom": "1rem",
                            },
                        ),
                        dash_table.DataTable(
                            id="pf_analysis",
                            columns=[
                                {
                                    "name": i,
                                    "id": i,
                                }
                                for i in (
                                    [
                                        "var",
                                        "coef",
                                        "std err",
                                        "t",
                                        "P>|t|",
                                        "[0.025",
                                        "0.975]",
                                    ]
                                )
                            ],
                            style_table={
                                "maxHeight": "300px",
                                "overflowY": "scroll",
                                "width": "100%",
                                "minWidth": "100%",
                                "margin": "0px",
                                "font-size": "14px",
                                "font-family": font,
                                "color": "#333333",
                                "background-color": "white",
                            },
                            style_cell={
                                "minWidth": "0px",
                                "maxWidth": "180px",
                                "width": "180px",
                                "height": "auto",
                                "whiteSpace": "normal",
                                "textAlign": "center",
                                "font-size": "14px",
                                "font-family": font,
                                "color": "#333333",
                                "background-color": "white",
                            },
                            style_data={
                                "border": "1px solid #ddd",
                                "font-size": "14px",
                                "font-family": font,
                                "color": "#333333",
                                "background-color": "white",
                            },
                            style_data_conditional=[
                                {
                                    "if": {
                                        "filter_query": "{P>|t|} < 0.05",
                                    },
                                    "backgroundColor": color_1,
                                    "fontColor": bar_color,
                                    "fontWeight": "bold",
                                },
                                {
                                    "if": {
                                        "filter_query": "{P>|t|} < 0.05 && {var} = const",
                                    },
                                    "backgroundColor": color_2,
                                    "fontColor": "	#FFFFFF",
                                    "fontWeight": "bold",
                                },
                            ],
                        ),
                    ],
                    width="auto",
                    sm=True,
                ),
                dbc.Col(
                    dcc.Graph(id="portfolio-returns"),
                    width=8,
                    xl=True,
                ),
            ]
        ),
    ],
)


@callback(
    Output("portfolio-returns", "figure"),
    Output("pf_analysis", "data"),
    Output("mean-portfolio-returns", "children"),
    Input("symbol-input", "value"),
)
def update_stock_returns_graph(symbols: str):
    benchmark = "VOO"
    interval = "1mo"
    if not symbols:
        symbols = ["VOO"]

    # Portfolio performance
    df = fetch_stock_returns(
        symbols, interval=interval, return_format="cumulative_percentage"
    )

    # Create Portfolio Analysis object
    pf_analysis = PortfolioAnalysis(
        cumulative_returns=df, benchmark_portfolio=benchmark, interval=interval
    )

    pf_analysis.graph = create_performance_graph(pf_analysis)

    return (
        pf_analysis.graph,
        pf_analysis.run_portfolio_analysis().to_dict("records"),
        pf_analysis.mean_returns_str,
    )

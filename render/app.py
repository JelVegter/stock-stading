# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, dash_table
import plotly.express as px
from src.analysis import portfolio_analysis as pa
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from pandas import DataFrame
from dash_bootstrap_templates import load_figure_template


# Colors
color_1 = "#f3f3f1"
color_2 = "#a2a292"
color_3 = "#848586"
color_4 = "#C2847A"
color_5 = "#280003"

font_color = "#f8f8ff"
bar_bgcolor = "#b0bec5"  # material blue-gray 200
bar_unselected_color = "#78909c"  # material blue-gray 400
bar_color = "#546e7a"  # material blue-gray 600
bar_selected_color = color_5  # material blue-gray 800
bar_unselected_opacity = 0.8

# Fonts
font = "Arial"

# Content
CONTENT_STYLE = {
    "margin-left": "5rem",
    "margin-right": "5rem",
    "padding": "2rem 1rem",
}

# Figure template
row_heights = [150, 300, 350]
template = {"layout": {"paper_bgcolor": color_1, "plot_bgcolor": color_1}}


def create_performance_graph(df: DataFrame):
    df = df.rename(
        columns={
            "cumulative_returns_percentage": "Cumulative Returns",
            "cumulative_returns_percentage_benchmark": "Cumulative Returns SP500",
        }
    )
    fig = px.line(
        df,
        x="date",
        y=["Cumulative Returns", "Cumulative Returns SP500"],
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
app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])

load_figure_template("ZEPHYR")

app.layout = html.Div(
    style=CONTENT_STYLE,
    children=[
        html.H1(
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
                            options=pa.get_available_symbols(),
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


@app.callback(
    Output("portfolio-returns", "figure"),
    Output("pf_analysis", "data"),
    Output("mean-portfolio-returns", "children"),
    Input("symbol-input", "value"),
)
def update_stock_returns_graph(symbols: str):

    # Benchmark performance
    sp500_performance = pa.get_sp500_performance()

    # Portfolio performance
    pf_analysis = pa.get_portfolio_performance(symbols)

    # Combine in graph
    portfolio_returns = pa.combine_portfolio_performance_with_benchmark(
        pf_analysis.history, sp500_performance
    )
    pf_analysis.graph = create_performance_graph(portfolio_returns)

    return (
        pf_analysis.graph,
        pf_analysis.analysis.to_dict("records"),
        pf_analysis.mean_returns_str,
    )


if __name__ == "__main__":
    app.run_server(debug=True)

import dash
from dash import html, dcc, callback, Input, Output, dash_table
from render.style import CONTENT_STYLE, font_color
import dash_bootstrap_components as dbc
from src.analysis import portfolio_analysis as pa
from src.analysis import efficient_frontier as ef
from src.etl import get_available_symbols
import pandas as pd
import plotly.express as px
from render.style import (
    template,
    font,
    font_color,
    CONTENT_STYLE,
    color_1,
    color_2,
    bar_color,
)

dash.register_page(__name__)


def create_efficient_frontier_graph(df: pd.DataFrame):
    dict_df = df.to_dict()
    for col in df.columns:
        df[col] = df[col].astype(float)
    df = pd.DataFrame.from_dict(dict_df, orient="columns")
    nr_of_assets = len(df.columns) - 2
    portfolio_weights = df.iloc[:, :nr_of_assets]
    fig = px.scatter(
        df,
        x=df["portfolio_std_dev"],
        y=df["portfolio_return"],
        hover_data=portfolio_weights,
        color="sharpe_ratio",
        color_continuous_scale="balance",
        # color_continuous_scale="ylorbr",
        # size=np.ones(results.shape[1]) * 10,
        opacity=0.3,
        template=template,
    )

    for col in df.columns:
        df[col] = df[col].astype(float)

    pf_high_sharpe = df.iloc[df["sharpe_ratio"].idxmax()]
    pf_high_sharpe_weights = pf_high_sharpe.iloc[:nr_of_assets]
    pf_hgh_return = df.iloc[df["portfolio_return"].idxmax()]
    pf_low_variance = df.iloc[df["portfolio_std_dev"].idxmax()]
    fig.add_scatter(
        x=[pf_high_sharpe["portfolio_std_dev"]],
        y=[pf_high_sharpe["portfolio_return"]],
        mode="markers",
        hovertext=pf_high_sharpe,
        marker=dict(size=15, color="red", symbol="star"),
        name="Max Sharpe ratio",
    )
    # fig.add_scatter(
    #     x=[pf_hgh_return["portfolio_std_dev"]],
    #     y=[pf_hgh_return["portfolio_return"]],
    #     mode="markers",
    #     marker=dict(size=45, color="red"),
    #     name="Max Returns",
    # )
    # fig.add_scatter(
    #     x=[pf_low_variance["portfolio_std_dev"]],
    #     y=[pf_low_variance["portfolio_return"]],
    #     mode="markers",
    #     marker=dict(size=45, color="red"),
    #     name="Min Variance",
    # )
    fig.update_layout(coloraxis_colorbar=dict(yanchor="top", ticks="outside"))
    fig.update_layout(
        title="Simulated portfolios - efficient frontier",
        xaxis_title="annualized volatility",
        yaxis_title="annualized returns",
    )
    return fig


layout = html.Div(
    children=[
        html.H2(
            children="Markowitz Modern Portfolio Theory - Efficient Frontier",
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
                            id="Asset Allocation",
                            children="Optimal Portfolio Allocation",
                            style={
                                "margin-top": "2rem",
                                "margin-bottom": "1rem",
                            },
                        ),
                        dash_table.DataTable(
                            id="optimal-portfolio-allocation",
                            columns=[
                                {
                                    "name": i,
                                    "id": i,
                                }
                                for i in (["Asset", "Allocation %"])
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
                        ),
                        html.Div(
                            children="Portfolio Metrics",
                            id="optimal-portfolio-metrics",
                            style={
                                "margin-top": "2rem",
                                "margin-bottom": "1rem",
                            },
                        ),
                        dash_table.DataTable(
                            id="optimal-portfolio-metrics",
                            columns=[
                                {
                                    "name": i,
                                    "id": i,
                                }
                                for i in (["Metric", "Value"])
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
                        ),
                    ]
                ),
                dbc.Col(
                    dcc.Graph(id="efficient-frontier"),
                    width=8,
                    xl=True,
                ),
            ],
        ),
    ],
)


@callback(
    Output("efficient-frontier", "figure"),
    Output("optimal-portfolio-allocation", "data"),
    Output("optimal-portfolio-metrics", "data"),
    Input("symbol-input", "value"),
)
def calculate_efficient_frontier(symbols: list[str]):
    if not symbols:
        symbols = ["VOO", "VTI", "VTIP", "VNQ"]

    df = ef.calculate_efficient_frontier(symbols)

    max_sharpe = df.iloc[df["sharpe_ratio"].idxmax()]
    max_sharpe = max_sharpe.reset_index()

    # portfolio table
    pf_allocation = max_sharpe.iloc[: len(symbols)].copy()
    pf_allocation.columns = ["Asset", "Allocation %"]
    pf_allocation["Allocation %"] = round(pf_allocation["Allocation %"], 2) * 100

    # evaluation table
    pf_metrics = max_sharpe.iloc[len(symbols) :].copy()
    pf_metrics.columns = ["Metric", "Value"]
    pf_metrics["Value"] = round(pf_metrics["Value"], 2)

    # fig
    efficient_frontier = create_efficient_frontier_graph(df)
    optimal_portfolio_allocation = pf_allocation.to_dict("records")
    optimal_portfolio_metrics = pf_metrics.to_dict("records")
    return efficient_frontier, optimal_portfolio_allocation, optimal_portfolio_metrics

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import polars as pl
from dash import dash_table, dcc, html

from df_exp.graphs import GRAPHS_DICT


def generate_layout(df: pd.DataFrame | pl.DataFrame) -> dbc.Container:
    """
    Generate the layout body as a container with two tabs, one for the graph and one for the table, each with a two column layout
    """
    body = dbc.Container(
        [
            html.Div(id="test-output"),
            dbc.Tabs(
                [
                    generate_graph_tab(df),
                    generate_table_tab(df),
                ]
            ),
        ]
    )

    return body


def generate_layout_test(df: pd.DataFrame | pl.DataFrame) -> dbc.Container:
    """
    Generate the layout body as a container with two tabs, one for the graph and one for the table, each with a two column layout
    """
    body = dbc.Container(
        [dbc.Tabs([dbc.Tab(label="T1", children=[]), dbc.Tab(label="T2", children=[])])]
    )

    return body


def generate_graph_tab(df: pd.DataFrame | pl.DataFrame) -> dbc.Tab:
    tab = dbc.Tab(
        label="Graph",
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                id="graph_controls",
                                children=[generate_graph_controls(df)],
                            )
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="graph-div",
                                style={"height": "90%"},
                            )
                        ],
                        width=10,
                    ),
                ]
            )
        ],
    )
    return tab


def generate_table_tab(df: pd.DataFrame | pl.DataFrame) -> dbc.Tab:
    tab = dbc.Tab(
        label="Table",
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                id="table_controls",
                                children=[generate_table_controls(df)],
                            )
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            # start with default 10 rows
                            html.Div(
                                id="table-div",
                                children=[
                                    dash_table.DataTable(
                                        (
                                            df.to_dict("records")[:10]
                                            if isinstance(df, pd.DataFrame)
                                            else df.to_pandas()[:10].to_dict("records")
                                        ),
                                        id="table",
                                    )
                                ],
                            ),
                        ],
                        width=10,
                    ),
                ]
            )
        ],
    )

    return tab


def generate_table_controls(df: pd.DataFrame | pl.DataFrame) -> dbc.Card:
    """For the first iteration only have a filter and a max row"""
    layout = dbc.Card(
        [
            dbc.Label("Max rows"),
            dcc.Input(
                id="max-rows",
                className="table_control",
                type="number",
                value=10,
                style={"width": "100%"},
                min=0,
                max=len(df),
            ),
            dbc.Label("Filter query"),
            html.Div(
                dcc.Textarea(
                    id="filter-table-text",
                    className="table_control",
                    placeholder="Any filter for df.query(...)",
                    style={"width": "100%", "height": "100px"},
                )
            ),
        ]
    )

    return layout


def generate_graph_controls(df: pd.DataFrame | pl.DataFrame) -> dbc.Card:
    layout = dbc.Card(
        [
            dbc.Label("Graph type"),
            dcc.Dropdown(
                id="graph-type",
                options=[
                    {"label": k, "value": k}  # cannot use the python objects here!
                    for k in GRAPHS_DICT.keys()
                ],
                value="Scatter",
            ),
            html.Div(id="graph-params", children=generate_graph_params_controls(df)),
            dbc.Label("Filter query"),
            html.Div(
                dcc.Textarea(
                    id="filter-graph-text",
                    placeholder="Any filter for df.query(...)",
                    style={"width": "100%", "height": "100px"},
                )
            ),
        ]
        + [
            dbc.Label("Graph template"),
            dcc.Dropdown(
                id="graph-template",
                options=[{"label": k, "value": k} for k in pio.templates.keys()],
                value="plotly_white",
            ),
        ]
    )
    return layout


def generate_graph_params_controls(
    df: pd.DataFrame | pl.DataFrame,
    graph_type_name: str = "Scatter",
    params_defaults: dict = None,  # used to overwrite in already existing
) -> list[html.Div]:
    params = GRAPHS_DICT[graph_type_name]["params"]
    cols = df.columns if isinstance(df, pl.DataFrame) else list(df.columns)

    controls = []
    for k, v in params.items():
        controls.append(dbc.Label(k))

        if v is None:
            # default to a dropdown
            controls.append(
                dcc.Dropdown(
                    id={"type": "graph_control", "index": k},
                    options=cols + [None],
                    value=params_defaults.get(k, None) if params_defaults else v,
                )
            )
        elif isinstance(v, int):
            # allow any int with an input
            controls.append(
                dcc.Input(
                    id={"type": "graph_control", "index": k},
                    type="number",
                    value=params_defaults.get(k, v) if params_defaults else v,
                )
            )

    # add a generic addition kwargs section accepting any dict as valid json str
    controls.append(dbc.Label("Additional kwargs"))
    controls.append(
        dcc.Textarea(
            id="additional-graph-kwargs",
            placeholder='Any kwargs as valid json, e.g., {"size": 5}',
            style={"width": "100%", "height": "100px"},
        )
    )

    return controls

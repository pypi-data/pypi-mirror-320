# Defining the available graphs and options for plotting via plotly express
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl

GRAPHS_DICT = {
    "Scatter": {
        "graph_func": px.scatter,
        "params": {  # a free text field will also allow to add any other kwargs
            "x": None,
            "y": None,
            "color": None,
            "size": None,
            "facet_col": None,
            "facet_row": None,
        },
    },
    "Line": {
        "graph_func": px.line,
        "params": {  # a free text field will also allow to add any other kwargs
            "x": None,
            "y": None,
            "color": None,
            "facet_col": None,
            "facet_row": None,
        },
    },
    "Bar": {
        "graph_func": px.bar,
        "params": {
            "x": None,
            "y": None,
            "color": None,
            "facet_col": None,
            "facet_row": None,
        },
    },
    "Box": {
        "graph_func": px.box,
        "params": {
            "x": None,
            "y": None,
            "color": None,
            "facet_col": None,
            "facet_row": None,
        },
    },
    "Histogram": {
        "graph_func": px.histogram,
        "params": {
            "x": None,
            "y": None,
            "color": None,
            "facet_col": None,
            "facet_row": None,
        },
    },
}


def plot_graph(
    df: pl.DataFrame | pd.DataFrame, plot_name: str = "Scatter", **kwargs
) -> go.Figure():
    fig_func = GRAPHS_DICT[plot_name]["graph_func"]

    fig = fig_func(df, **kwargs)

    # adjust layout to ensure proper height

    return fig

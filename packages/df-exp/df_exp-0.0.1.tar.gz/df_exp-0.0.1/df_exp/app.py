# The basic app will have two tabs, one for a graph the other for a table + basic summary

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import polars as pl

from df_exp.callbacks import add_callbacks
from df_exp.layouts import generate_layout


def init_app(df: pd.DataFrame | pl.DataFrame) -> dash.Dash:
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = generate_layout(df)
    app = add_callbacks(app, df)

    return app


def show(df: pd.DataFrame | pl.DataFrame, debug: bool = False):
    """The basic method to spawn the app to show info for a data frame"""
    app = init_app(df)

    app.run_server(debug=False)


if __name__ == "__main__":

    import numpy as np

    df = pl.DataFrame(
        {
            "a": np.arange(10),
            "b": np.random.rand(10),
            "c": np.random.choice(["aa", "bb", "cc"], 10),
            "d": np.linspace(0, 1, 10),
        }
    )

    show(df)

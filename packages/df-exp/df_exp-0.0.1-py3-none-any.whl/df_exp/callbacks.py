import json

import pandas as pd
import polars as pl
from dash import ALL, Dash, Input, Output, State, dash_table

from df_exp.graphs import plot_graph
from df_exp.layouts import generate_graph_params_controls


def add_callbacks(app: Dash, df: pl.DataFrame | pd.DataFrame) -> Dash:
    """Add all callbacks for functionality"""

    @app.callback(
        Output("graph-params", "children"),
        [
            Input("graph-type", "value"),
        ],
        [
            State({"type": "graph_control", "index": ALL}, "id"),
            State({"type": "graph_control", "index": ALL}, "value"),
        ],
    )
    def update_controls(graph_type: str, *values_and_ids):

        ids = [d["index"] for d in values_and_ids[0]]
        curr_params = dict(zip(ids, values_and_ids[1]))

        return generate_graph_params_controls(
            df, graph_type_name=graph_type, params_defaults=curr_params
        )

    @app.callback(
        Output("graph-div", "figure"),
        [
            State("graph-type", "n_blur"),
            Input("graph-template", "value"),
            Input(
                "filter-graph-text", "n_blur"
            ),  # number of times this went out of focus -> to trigger the callback not while writing
            Input("additional-graph-kwargs", "n_blur"),
            Input({"type": "graph_control", "index": ALL}, "id"),
            Input({"type": "graph_control", "index": ALL}, "value"),
        ],
        [
            State("graph-type", "value"),
            State("filter-graph-text", "value"),
            State("additional-graph-kwargs", "value"),
        ],
    )
    def update_graph(
        graph_type_nblur: int,
        graph_template: str,
        filter_query_nblur: int,
        kwargs_string_nblur: int,
        *values_and_ids,
    ):
        graph_type = values_and_ids[-3]
        filter_query = values_and_ids[-2]
        kwargs_string = values_and_ids[-1]

        if df is None:
            return {}

        dp = df.to_pandas() if isinstance(df, pl.DataFrame) else df
        if filter_query != "" and filter_query is not None:
            dp = dp.query(filter_query)

        kwargs = {
            "plot_name": graph_type,
            "template": graph_template,
        }

        if kwargs_string is not None and kwargs_string != "":
            try:
                kwargs.update(json.loads(kwargs_string))
            except TypeError:
                breakpoint()

        ids = [d["index"] for d in values_and_ids[0]]
        kwargs.update(dict(zip(ids, values_and_ids[1])))

        if kwargs["x"] is None and kwargs["y"] is None:
            return {}

        return plot_graph(dp, **kwargs)

    # update the table view
    @app.callback(
        Output("table-div", "children"),
        [
            Input("max-rows", "value"),
        ],
    )
    def update_table(max_rows: int):
        tbl = dash_table.DataTable(
            (
                df.to_dict("records")[:max_rows]
                if isinstance(df, pd.DataFrame)
                else df.to_pandas()[:max_rows].to_dict("records")
            ),
            id="table",
        )
        return tbl

    return app

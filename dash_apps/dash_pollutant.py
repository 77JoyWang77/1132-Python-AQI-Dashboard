import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

def create_dash_pollutant_app(server):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_pollutant/',
        suppress_callback_exceptions=True
    )

    with sqlite3.connect("data/aqi_history.db") as conn:
        sites = pd.read_sql("SELECT DISTINCT sitename, siteid FROM aqi ORDER BY siteid", conn)
        site_options = sites["sitename"].tolist()
        years = pd.read_sql("SELECT DISTINCT year FROM aqi ORDER BY year DESC", conn)
        year_options = years["year"].tolist()

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇年份："),
                dcc.Dropdown(
                    id="year-pollutant",
                    options=[{"label": y, "value": y} for y in year_options],
                    value=year_options[0]
                )
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),

            html.Div([
                html.Label("選擇測站："),
                dcc.Dropdown(
                    id="site-pollutant",
                    options=[{"label": s, "value": s} for s in site_options],
                    value=site_options[0]
                )
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="pollutant-composition-bar")
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    @dash_app.callback(
        Output("pollutant-composition-bar", "figure"),
        Input("year-pollutant", "value"),
        Input("site-pollutant", "value")
    )
    def pollutant_stack(year, site):
        with sqlite3.connect("data/aqi_history.db") as conn:
            sql = """
            SELECT month, mainpollutant
            FROM aqi
            WHERE year=? AND sitename=? AND mainpollutant != '-1'
            """
            dff = pd.read_sql(sql, conn, params=[year, site])
        if dff.empty:
            return px.bar(title="查無資料")
        count_df = dff.groupby(["month", "mainpollutant"]).size().reset_index(name="count")
        return px.bar(
            count_df,
            x="month", y="count", color="mainpollutant",
            title=f"{year} 年各月主污染物構成 - {site}",
            barmode="stack",
            category_orders={"month": [str(i) for i in range(1, 13)]}
        )
    return dash_app

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

def create_dash_aqiyear_app(server):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_aqiyear/',
        suppress_callback_exceptions=True
    )

    with sqlite3.connect("data/aqi_history.db") as conn:
        sites = pd.read_sql("SELECT DISTINCT sitename, siteid FROM aqi ORDER BY siteid", conn)
        site_options = sites["sitename"].tolist()

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇測站："),
                dcc.Dropdown(
                    id="site-diff",
                    options=[{"label": s, "value": s} for s in site_options],
                    value=site_options[0]
                )
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="yearly-change-bar"),
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    @dash_app.callback(
        Output("yearly-change-bar", "figure"),
        Input("site-diff", "value")
    )
    def yearly_diff(site):
        with sqlite3.connect("data/aqi_history.db") as conn:
            sql = "SELECT year, AVG(aqi) as aqi FROM aqi WHERE sitename=? GROUP BY year"
            year_avg = pd.read_sql(sql, conn, params=[site])
        if year_avg.empty:
            return px.bar(title="查無資料")
        year_avg = year_avg.sort_values("year")
        year_avg["diff"] = year_avg["aqi"].diff()
        diffs = year_avg.dropna()
        if diffs.empty:
            return px.bar(title="查無資料")
        return px.bar(
            diffs,
            x="year", y="diff",
            title=f"每年 AQI 變化 - {site}",
            labels={"year": "年", "diff": "AQI 差異值"}
        )
    return dash_app

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

def create_dash_month_app(server):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_month/',
        suppress_callback_exceptions=True
    )

    # 只抓選項
    with sqlite3.connect("data/aqi_history.db") as conn:
        years = pd.read_sql("SELECT DISTINCT year FROM aqi ORDER BY year DESC", conn)["year"].tolist()
        sites = pd.read_sql("SELECT DISTINCT sitename, siteid FROM aqi ORDER BY siteid", conn)["sitename"].tolist()
    site_options = [{"label": "全部", "value": "all"}] + [{"label": s, "value": s} for s in sites]

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇年份："),
                dcc.Dropdown(
                    id="year-month",
                    options=[{"label": y, "value": y} for y in years],
                    value=years[0]
                )
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),

            html.Div([
                html.Label("選擇測站："),
                dcc.Dropdown(
                    id="site-month",
                    options=site_options,
                    value="all"
                )
            ], style={"flex": 1, "minWidth": "100px"})
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="box-month")
    ], style={"padding": "20px"})

    @dash_app.callback(
        Output("box-month", "figure"),
        Input("year-month", "value"),
        Input("site-month", "value"))
    def update_box(year, site):
        with sqlite3.connect("data/aqi_history.db") as conn:
            if site == "all":
                df = pd.read_sql(
                    "SELECT month, aqi FROM aqi WHERE year=?",
                    conn, params=[year])
            else:
                df = pd.read_sql(
                    "SELECT month, aqi FROM aqi WHERE year=? AND sitename=?",
                    conn, params=[year, site])
        if df.empty:
            return px.box(title="查無資料")
        # month 做排序，避免亂序
        df["month"] = df["month"].astype(int).astype(str)
        df = df[df["month"].isin([str(i) for i in range(1, 13)])]
        return px.box(
            df, x="month", y="aqi",
            title=f"{year} 各月 AQI 分佈",
            category_orders={"month": [str(i) for i in range(1, 13)]}
        )

    return dash_app

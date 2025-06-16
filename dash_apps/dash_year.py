# dash_year.py
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

def create_dash_year_app(server):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_year/',
        suppress_callback_exceptions=True
    )

    # 只抓選項，不讀整包資料
    with sqlite3.connect("data/aqi_history.db") as conn:
        years = pd.read_sql("SELECT DISTINCT year FROM aqi ORDER BY year DESC", conn)["year"].tolist()
        sites = pd.read_sql("SELECT DISTINCT sitename, siteid FROM aqi ORDER BY siteid", conn)["sitename"].tolist()
    site_options = [{"label": s, "value": s} for s in sites]
    site_options = [{"label": "全部", "value": "all"}] + site_options

    # ★ 加入「全部」月份
    month_options = [{"label": "全部", "value": "all"}] + [{"label": f"{i} 月", "value": str(i)} for i in range(1, 13)]

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇月份："),
                dcc.Dropdown(
                    id="month-year",
                    options=month_options,
                    value="all"
                )
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),
            html.Div([
                html.Label("選擇測站："),
                dcc.Dropdown(
                    id="site-year",
                    options=site_options,
                    value="all"
                )
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="box-year")
    ], style={"padding": "20px"})

    @dash_app.callback(
        Output("box-year", "figure"),
        Input("month-year", "value"),
        Input("site-year", "value")
    )
    def update_box_year(month, site):
        with sqlite3.connect("data/aqi_history.db") as conn:
            query = "SELECT year, aqi FROM aqi"
            params = []
            conds = []
            if month != "all":
                conds.append("month=?")
                params.append(month)
            if site != "all":
                conds.append("sitename=?")
                params.append(site)
            if conds:
                query += " WHERE " + " AND ".join(conds)
            df = pd.read_sql(query, conn, params=params)
        if df.empty:
            return px.box(title="查無資料")
        title = "各年 AQI 分佈"
        if month != "all":
            title = f"{int(month)}月 " + title
        return px.box(df, x="year", y="aqi", title=title)

    return dash_app
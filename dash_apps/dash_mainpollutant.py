import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

def create_dash_mainpollutant_app(server):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_mainpollutant/',
        suppress_callback_exceptions=True
    )

    # 只抓選項
    with sqlite3.connect("data/aqi_history.db") as conn:
        years = pd.read_sql("SELECT DISTINCT year FROM aqi ORDER BY year DESC", conn)["year"].tolist()
        sites = pd.read_sql("SELECT DISTINCT sitename, siteid FROM aqi ORDER BY siteid", conn)["sitename"].tolist()
    year_options = [{"label": "全部", "value": "all"}] + [{"label": y, "value": y} for y in years]
    month_options = [{"label": f"{i} 月", "value": str(i)} for i in range(1, 13)]
    site_options = [{"label": "全部", "value": "all"}] + [{"label": s, "value": s} for s in sites]

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇年份："),
                dcc.Dropdown(
                    id="year-pollutant",
                    options=year_options,
                    value=years[0]
                )
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),
            html.Div([
                html.Label("選擇月份："),
                dcc.Dropdown(
                    id="month-pollutant",
                    options=month_options,
                    value="1"
                )
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),
            html.Div([
                html.Label("選擇測站："),
                dcc.Dropdown(
                    id="site-pollutant",
                    options=site_options,
                    value="all"
                )
            ], style={"flex": 1, "minWidth": "100px"})
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="box-mainpollutant")
    ], style={"padding": "20px"})

    @dash_app.callback(
        Output("box-mainpollutant", "figure"),
        Input("year-pollutant", "value"),
        Input("month-pollutant", "value"),
        Input("site-pollutant", "value"))
    def update_box(year, month, site):
        sql = "SELECT mainpollutant, aqi FROM aqi WHERE mainpollutant != '-1'"
        params = []
        if year != "all":
            sql += " AND year=?"
            params.append(year)
        if month:
            sql += " AND month=?"
            params.append(month)
        if site != "all":
            sql += " AND sitename=?"
            params.append(site)
        with sqlite3.connect("data/aqi_history.db") as conn:
            df = pd.read_sql(sql, conn, params=params)
        if df.empty:
            return px.box(title="查無資料")
        return px.box(df, x="mainpollutant", y="aqi", title="主污染物 AQI 分佈")

    return dash_app

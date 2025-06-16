# dash_site.py
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

def create_dash_site_app(server):
    dash_app = dash.Dash(
        __name__, 
        server=server, 
        url_base_pathname='/dash_site/', 
        suppress_callback_exceptions=True)
    
    with sqlite3.connect("data/aqi_history.db") as conn:
        years = pd.read_sql("SELECT DISTINCT year FROM aqi ORDER BY year DESC", conn)["year"].tolist()
        months = [str(i) for i in range(1, 13)]
    
    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇年份："),
                dcc.Dropdown(
                    id="year",
                    options=[{"label": y, "value": y} for y in years],
                    value=years[0]
                )
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),

            html.Div([
                html.Label("選擇月份："),
                dcc.Dropdown(
                    id="month",
                    options=[{"label": m, "value": m} for m in months],
                    value=months[0]
                )
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="box-site")
    ], style={"padding": "20px"})
    
    @dash_app.callback(
        Output("box-site", "figure"),
        Input("year", "value"),
        Input("month", "value"))
    def update_box(year, month):
        with sqlite3.connect("data/aqi_history.db") as conn:
            df = pd.read_sql("SELECT sitename, aqi FROM aqi WHERE year=? AND month=?", conn, params=[year, month])
        if df.empty:
            return px.box(title="查無資料")
        return px.box(df, x="sitename", y="aqi", title=f"{year}年{int(month)}月 各測站 AQI 分佈")
    return dash_app

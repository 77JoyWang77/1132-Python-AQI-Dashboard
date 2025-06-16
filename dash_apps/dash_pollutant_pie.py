# dash_pollutant_pie.py
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

def create_dash_pollutant_pie_app(server):
    # 先抓選項（只撈 site, year，不撈大表）
    with sqlite3.connect("data/aqi_history.db") as conn:
        years = pd.read_sql("SELECT DISTINCT year FROM aqi ORDER BY year DESC", conn)["year"].tolist()
        sites = pd.read_sql("SELECT DISTINCT sitename FROM aqi ORDER BY sitename", conn)["sitename"].tolist()
    site_options = [{"label": "全部", "value": "all"}] + [{"label": s, "value": s} for s in sites]
    year_options = [{"label": "全部", "value": "all"}] + [{"label": y, "value": y} for y in years]
    month_options = [{"label": "全部", "value": "all"}] + [{"label": f"{i} 月", "value": str(i)} for i in range(1, 13)]

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_pollutant_pie/',
        suppress_callback_exceptions=True
    )
    dash_app.title = "主污染物圓餅圖"

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇年份："),
                dcc.Dropdown(id="year-dropdown", options=year_options, value=years[0])
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),
            html.Div([
                html.Label("選擇月份："),
                dcc.Dropdown(id="month-dropdown", options=month_options, value="all")
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),
            html.Div([
                html.Label("選擇測站："),
                dcc.Dropdown(id="site-dropdown", options=site_options, value="all")
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "30px"}),
        dcc.Graph(id="pollutant-pie")
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    @dash_app.callback(
        Output("pollutant-pie", "figure"),
        Input("year-dropdown", "value"),
        Input("month-dropdown", "value"),
        Input("site-dropdown", "value")
    )
    def update_pollutant_pie(year, month, site):
        query = "SELECT mainpollutant FROM aqi WHERE mainpollutant != '-1'"
        params = []
        if year != "all":
            query += " AND year=?"
            params.append(year)
        if month != "all":
            query += " AND month=?"
            params.append(month)
        if site != "all":
            query += " AND sitename=?"
            params.append(site)
        with sqlite3.connect("data/aqi_history.db") as conn:
            dff = pd.read_sql(query, conn, params=params)
        if dff.empty:
            return px.pie(names=["查無資料"], values=[1], title="主污染物佔比")
        return px.pie(
            dff,
            names="mainpollutant",
            title="主污染物佔比",
            color_discrete_sequence=px.colors.sequential.Viridis
        )

    return dash_app

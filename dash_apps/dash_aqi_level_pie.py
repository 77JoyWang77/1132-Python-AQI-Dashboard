import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

aqi_levels = [
    (0, 50, "#00E400", "良好"),
    (51, 100, "#FFFF00", "普通"),
    (101, 150, "#FF7E00", "對敏感族群不健康"),
    (151, 200, "#FF0000", "不健康"),
    (201, 300, "#8F3F97", "非常不健康"),
    (301, 500, "#7E0023", "危害")
]
aqi_color_map = {level[3]: level[2] for level in aqi_levels}

def get_aqi_level(aqi):
    if aqi <= 50: return "良好"
    elif aqi <= 100: return "普通"
    elif aqi <= 150: return "對敏感族群不健康"
    elif aqi <= 200: return "不健康"
    elif aqi <= 300: return "非常不健康"
    else: return "危害"

def create_dash_aqi_level_pie_app(server):
    with sqlite3.connect("data/aqi_history.db") as conn:
        years = pd.read_sql("SELECT DISTINCT year FROM aqi ORDER BY year DESC", conn)["year"].tolist()
        sites = pd.read_sql("SELECT DISTINCT sitename FROM aqi ORDER BY sitename", conn)["sitename"].tolist()
    site_options = [{"label": "全部", "value": "all"}] + [{"label": s, "value": s} for s in sites]
    year_options = [{"label": "全部", "value": "all"}] + [{"label": y, "value": y} for y in years]
    month_options = [{"label": "全部", "value": "all"}] + [{"label": f"{i} 月", "value": str(i)} for i in range(1, 13)]

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_aqi_level_pie/',
        suppress_callback_exceptions=True
    )
    dash_app.title = "AQI 等級圓餅圖"

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
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="aqi-level-pie")
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    @dash_app.callback(
        Output("aqi-level-pie", "figure"),
        Input("year-dropdown", "value"),
        Input("month-dropdown", "value"),
        Input("site-dropdown", "value")
    )
    def update_pie(year, month, site):
        query = "SELECT aqi FROM aqi WHERE 1=1"
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
            return px.pie(names=["查無資料"], values=[1], title="AQI 危險等級佔比")
        dff["AQI 等級"] = dff["aqi"].apply(get_aqi_level)
        return px.pie(
            dff,
            names="AQI 等級",
            title="AQI 危險等級佔比",
            color="AQI 等級",
            color_discrete_map=aqi_color_map
        )
    return dash_app

# dash_calendar.py
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import sqlite3

def create_dash_calendar_app(server):
    # 預抓站名與每站可選年份
    with sqlite3.connect("data/aqi_history.db") as conn:
        df_opt = pd.read_sql("SELECT DISTINCT sitename, year FROM aqi", conn)
    site_options = sorted(df_opt["sitename"].unique())
    year_dict = {site: sorted(df_opt[df_opt["sitename"] == site]["year"].unique(), reverse=True) for site in site_options}
    default_site = site_options[0]
    default_year = year_dict[default_site][0]

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_calendar/',
        suppress_callback_exceptions=True
    )
    dash_app.title = "AQI 日曆熱圖"

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇測站："),
                dcc.Dropdown(id="site-dropdown", options=[{"label": s, "value": s} for s in site_options], value=default_site)
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),
            html.Div([
                html.Label("選擇年份："),
                dcc.Dropdown(id="year-dropdown")
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),
            html.Div([
                html.Label("選擇污染物指標："),
                dcc.Dropdown(
                    id="subindex-dropdown",
                    options=[
                        {"label": "AQI", "value": "aqi"},
                        {"label": "SO2", "value": "so2subindex"},
                        {"label": "CO", "value": "cosubindex"},
                        {"label": "PM10", "value": "pm10subindex"},
                        {"label": "NO2", "value": "no2subindex"},
                        {"label": "O3-8h", "value": "o38subindex"},
                        {"label": "PM2.5", "value": "pm25subindex"},
                    ],
                    value="aqi",
                    clearable=False,
                )
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="calendar-heatmap", style={"height": "850px"})
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    # 動態更新年份選單
    @dash_app.callback(
        Output("year-dropdown", "options"),
        Output("year-dropdown", "value"),
        Input("site-dropdown", "value")
    )
    def update_year_options(selected_site):
        years = year_dict[selected_site]
        return [{"label": y, "value": y} for y in years], years[0]

    @dash_app.callback(
        Output("calendar-heatmap", "figure"),
        Input("site-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input("subindex-dropdown", "value")
    )
    def update_heatmap(site, year, subindex):
        with sqlite3.connect("data/aqi_history.db") as conn:
            cols = "monitordate, " + subindex
            query = f"SELECT {cols} FROM aqi WHERE sitename=? AND year=?"
            df = pd.read_sql(query, conn, params=[site, year])

        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="查無資料", height=800)
            return fig

        df["monitordate"] = pd.to_datetime(df["monitordate"])
        df[subindex] = pd.to_numeric(df[subindex], errors="coerce")
        df = df.dropna(subset=[subindex])

        df["dow"] = df["monitordate"].dt.weekday
        df["week"] = df["monitordate"].dt.isocalendar().week
        df["month"] = df["monitordate"].dt.month
        df["text"] = df["monitordate"].dt.strftime("%Y-%m-%d") + "<br>" + f"{subindex}: " + df[subindex].astype(int).astype(str)

        df.loc[(df["month"] == 1) & (df["week"] > 50), "week"] = 0
        df.loc[(df["month"] == 12) & (df["week"] == 1), "week"] = df["week"].max() + 1

        colorscale = [
            [0.0, "#00e400"],
            [0.2, "#ffff00"],
            [0.4, "#ff7e00"],
            [0.6, "#ff0000"],
            [0.8, "#8f3f97"],
            [1.0, "#7e0023"]
        ]
        names = {
            "aqi": "AQI", "so2subindex": "SO2", "cosubindex": "CO",
            "pm10subindex": "PM10", "no2subindex": "NO2", "o38subindex": "O3-8h", "pm25subindex": "PM2.5"
        }
        pollutant_name = names.get(subindex, subindex.upper())
        zmax_val = 500

        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            x=df["dow"],
            y=df["week"],
            z=df[subindex],
            text=df["text"],
            hoverinfo="text",
            colorscale=colorscale,
            zmin=0, zmax=zmax_val,
        ))
        fig.update_layout(
            title=f"{site} 測站 {year} 年 {pollutant_name} 日曆熱圖",
            xaxis=dict(
                title="星期",
                tickmode="array",
                tickvals=list(range(7)),
                ticktext=["一", "二", "三", "四", "五", "六", "日"]
            ),
            yaxis=dict(title="週次", autorange="reversed"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="black"),
            margin=dict(t=60, b=40, l=60, r=20),
            height=800
        )
        return fig

    return dash_app

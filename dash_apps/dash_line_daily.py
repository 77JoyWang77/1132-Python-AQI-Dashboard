import dash 
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import sqlite3

def create_dash_line_daily_app(server):
    db_path = "data/aqi_history.db"
    with sqlite3.connect(db_path) as conn:
        sites = pd.read_sql("SELECT DISTINCT sitename FROM aqi ORDER BY sitename", conn)["sitename"].tolist()
        years = pd.read_sql("SELECT DISTINCT year FROM aqi ORDER BY year", conn)["year"].tolist()
    month_options = [{"label": f"{m} 月", "value": m} for m in range(1, 13)]

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_line_daily/',
        suppress_callback_exceptions=True
    )

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("測站"),
                dcc.Dropdown(
                    id="station-dropdown",
                    options=[{"label": s, "value": s} for s in sites],
                    value=sites[0],
                ),
            ], style={"flex": 1, "minWidth": "120px", "marginRight": "10px"}),
            html.Div([
                html.Label("年份"),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[{"label": y, "value": y} for y in years],
                    value=years[-1],
                ),
            ], style={"flex": 1, "minWidth": "100px", "marginRight": "10px"}),
            html.Div([
                html.Label("月份"),
                dcc.Dropdown(
                    id="month-dropdown",
                    options=month_options,
                    value=5,
                ),
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="aqi-line-chart")
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    @dash_app.callback(
        Output("aqi-line-chart", "figure"),
        Input("station-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input("month-dropdown", "value")
    )
    def update_chart(station, year, month):
        if not (station and year and month):
            return go.Figure(layout=go.Layout(title="查無資料"))
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql(
                """SELECT monitordate, aqi, so2subindex, cosubindex, pm10subindex, no2subindex, o38subindex, pm25subindex
                   FROM aqi WHERE sitename=? AND year=? AND month=?
                   ORDER BY monitordate""",
                conn, params=[station, year, month])
        if df.empty:
            return go.Figure(layout=go.Layout(title="查無資料", xaxis_title="日", yaxis_title="AQI"))

        # 轉成 datetime
        df["monitordate"] = pd.to_datetime(df["monitordate"], errors="coerce")
        # 過濾掉無效日期
        df = df.dropna(subset=["monitordate"])

        col_order = [
            ("aqi", "AQI", "#4CAF50"),
            ("so2subindex", "SO2", "#2196F3"),
            ("cosubindex", "CO", "#FFB74D"),
            ("pm10subindex", "PM10", "#BA68C8"),
            ("no2subindex", "NO2", "#E57373"),
            ("o38subindex", "O3", "#4DB6AC"),
            ("pm25subindex", "PM2.5", "#FFD54F"),
        ]

        fig = go.Figure()
        for col, name, color in col_order:
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["monitordate"], y=df[col], mode="lines+markers",
                    name=name,
                    line=dict(color=color, width=3 if col == "aqi" else 2, dash="solid" if col == "aqi" else "dot"),
                    visible=True if col == "aqi" else "legendonly"
                ))

        aqi_levels = [
            (0, 50, "#00E400"),
            (51, 100, "#FFFF00"),
            (101, 150, "#FF7E00"),
            (151, 200, "#FF0000"),
            (201, 300, "#8F3F97"),
            (301, 500, "#7E0023")
        ]
        shapes = [
            dict(type="rect", xref="paper", yref="y", x0=0, x1=1, y0=low, y1=high,
                fillcolor=color, opacity=0.2, layer="below", line_width=0)
            for low, high, color in aqi_levels
        ]
        fig.update_layout(
            title=dict(
                text=f"{station} {year}年{month}月 AQI 日變化",
                y=0.98
            ),
            xaxis_title="日期", yaxis_title="AQI",
            yaxis=dict(range=[0, 500]),
            margin={"t": 70, "b": 40, "l": 60, "r": 20},
            template="plotly_white", shapes=shapes,
            legend=dict(orientation="h", y=1, yanchor="bottom", x=1, xanchor="right",
                        bgcolor="rgba(0,0,0,0)", bordercolor="LightGray", borderwidth=1)
        )
        return fig

    return dash_app

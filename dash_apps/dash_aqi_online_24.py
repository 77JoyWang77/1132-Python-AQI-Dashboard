import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

def create_dash_aqi_online_24_app(server):
    # 載入資料
    df_24 = pd.read_csv("data/aqi24.csv")
    df_24["datacreationdate"] = pd.to_datetime(df_24["datacreationdate"])
    df_24 = df_24.sort_values("datacreationdate")
    stations = sorted(df_24["sitename"].unique())

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_aqi_online_24/',
        suppress_callback_exceptions=True
    )

    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇測站："),
                dcc.Dropdown(
                    id="station-dropdown",
                    options=[{"label": s, "value": s} for s in stations],
                    value=stations[0] if stations else None
                )
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="aqi-24-line")
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    @dash_app.callback(
        Output("aqi-24-line", "figure"),
        Input("station-dropdown", "value")
    )
    def update_chart(station):
        if not station:
            return go.Figure(layout=go.Layout(title="查無資料"))

        dff = df_24[df_24["sitename"] == station].sort_values("datacreationdate")
        if dff.empty:
            return go.Figure(layout=go.Layout(title="查無資料"))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dff["datacreationdate"],
            y=pd.to_numeric(dff["aqi"], errors="coerce"),
            mode="lines+markers",
            name=station,
            connectgaps=True,
            line=dict(color="#4CAF50", width=3)
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
            title=dict(text=f"{station} 過去24小時即時AQI變化", y=0.98),
            xaxis_title="時間", yaxis_title="AQI",
            yaxis=dict(range=[0, 500]),
            margin={"t": 60, "b": 40, "l": 60, "r": 20},
            shapes=shapes,
            template="plotly_white",
            # xaxis=dict(
            #     tickformat="%m-%d %H:%M",   # 顯示 "06-16 09:00"
            #     dtick=3600000 * 3,          # 每3小時一格（24hr有8格），改這可微調
            #     tickangle=0,
            #     showgrid=True,
            #     ticks="outside"
            # )
        )
        return fig

    return dash_app

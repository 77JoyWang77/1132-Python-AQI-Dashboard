import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

subindices = ['aqi', 'so2subindex', 'cosubindex', 'pm10subindex', 'no2subindex', 'o38subindex', 'pm25subindex']
names = ['AQI', 'SO2', 'CO', 'PM10', 'NO2', 'O3', 'PM2.5']
colors = ["#4CAF50", "#2196F3", "#FFB74D", "#BA68C8", "#E57373", "#4DB6AC", "#FFD54F"]

def create_dash_aqi_online_30_app(server):
    # 載入資料
    df = pd.read_csv("data/aqi30.csv")
    df["monitordate"] = pd.to_datetime(df["monitordate"])
    df = df.sort_values("monitordate")
    stations = sorted(df["sitename"].unique())
    
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_aqi_online_30/',
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
        dcc.Graph(id="aqi-30-line")
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    @dash_app.callback(
        Output("aqi-30-line", "figure"),
        Input("station-dropdown", "value")
    )
    def update_chart(site):
        if df.empty or not site:
            return go.Figure(layout=go.Layout(title="查無資料"))
        dff = df[df["sitename"] == site].sort_values("monitordate")   # <== 多這一行

        if dff.empty:
            return go.Figure(layout=go.Layout(title="查無資料"))

        fig = go.Figure()
        for j, sub in enumerate(subindices):
            if sub in dff:
                fig.add_trace(go.Scatter(
                    x=dff["monitordate"],
                    y=pd.to_numeric(dff[sub], errors="coerce"),
                    mode="lines+markers",
                    name=names[j],
                    connectgaps=True,
                    line=dict(color=colors[j % len(colors)], dash="solid" if sub == "aqi" else "dash"),
                    visible=True if sub == "aqi" else "legendonly"
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
                text=f"{site} 過去30天 AQI 與副指標",
                y=0.98
            ),
            xaxis_title="日期", yaxis_title="AQI", yaxis=dict(range=[0, 500]),
            margin={"t": 60, "b": 40, "l": 60, "r": 20},
            template="plotly_white", shapes=shapes,
            legend=dict(
                orientation="h", y=1, yanchor="bottom", x=1, xanchor="right",
                bgcolor="rgba(0,0,0,0)", bordercolor="LightGray", borderwidth=1)
        )
        return fig


    return dash_app

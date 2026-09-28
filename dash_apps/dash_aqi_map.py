import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import requests
import os

# API 基本參數
api_url = "https://data.moenv.gov.tw/api/v2"
dataset = "AQX_P_432"
format_type = "json"
api_key = os.environ.get("MOENV_API_KEY", "")  # 環境部 API key，從環境變數讀取
fields = {
    "aqi": {"label": "AQI", "column": "aqi", "unit": "", "scale": [0, 50, 100, 150, 200, 300, 400, 500]},
    "pm2.5": {"label": "PM2.5", "column": "pm2.5_avg", "unit": "μg/m³", "scale": [0, 12.4, 30.4, 50.4, 125.4, 225.4, 325.4, 500.4]},
    "pm10": {"label": "PM10", "column": "pm10_avg", "unit": "μg/m³", "scale": [0, 30, 75, 190, 354, 424, 504, 604]},
    "o3": {"label": "O₃", "column": "o3_8hr", "unit": "ppb", "scale": [0, 54, 70, 85, 105, 200]},
    "co": {"label": "CO", "column": "co_8hr", "unit": "ppm", "scale": [0, 4.4, 9.4, 12.4, 15.4, 30.4, 40.4, 50.4]},
    "so2": {"label": "SO₂", "column": "so2", "unit": "ppb", "scale": [0, 8, 65, 160, 304, 604, 804, 1004]},
    "no2": {"label": "NO₂", "column": "no2", "unit": "ppb", "scale": [0, 21, 100, 360, 649, 1249, 1649, 2049]},
}
bar_colors = ["#00E400", "#FFFF00", "#FF7E00", "#FF0000", "#8F3F97", "#7E0023", "#28000B"]

def make_colorscale(breakpoints):
    vmax = breakpoints[-1]
    scale = [[0.0, bar_colors[0]]]
    n = len(breakpoints) - 2
    for i in range(1, n):
        mid = (breakpoints[i] + breakpoints[i + 1]) / 2 / vmax
        scale.append([mid, bar_colors[i]])
    scale.append([1.0, bar_colors[n]])
    return scale
colorscales = {
    key: make_colorscale(info["scale"])
    for key, info in fields.items()
}

def fetch_latest_aqi():
    url = f"{api_url}/{dataset}?format={format_type}&limit=1000&api_key={api_key}"
    response = requests.get(url, timeout=10)
    records = response.json()["records"]
    df = pd.DataFrame(records)
    # 經緯度、數值欄都轉成 float
    for col in ["latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for info in fields.values():
        df[info["column"]] = pd.to_numeric(df[info["column"]], errors="coerce")
    return df

def create_dash_aqi_map_app(server):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_aqi_map/',
        suppress_callback_exceptions=True
    )
    pollutant_options = [
        {"label": info["label"], "value": key}
        for key, info in fields.items()
    ]
    dash_app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label("選擇汙染指標："),
                dcc.Dropdown(
                    id="pollutant-dropdown",
                    options=pollutant_options,
                    value="aqi"
                )
            ], style={"flex": 1, "minWidth": "100px"}),
        ], style={"display": "flex", "width": "100%", "alignItems": "center", "marginBottom": "20px"}),
        dcc.Graph(id="aqi-map", style={"height": "650px"}, config={"scrollZoom": True})
    ], style={"padding": "20px", "backgroundColor": "white", "color": "black"})

    @dash_app.callback(
        Output("aqi-map", "figure"),
        Input("pollutant-dropdown", "value")
    )
    def update_map(pollutant):
        info = fields[pollutant]
        cs = colorscales[pollutant]
        df = fetch_latest_aqi()
        df = df.dropna(subset=["latitude", "longitude", info["column"]])
        fig = go.Figure(go.Scattermapbox(
            lat=df["latitude"],
            lon=df["longitude"],
            mode="markers",
            marker=dict(
                size=13,
                color=df[info["column"]],
                colorscale=cs,
                cmin=info["scale"][0],
                cmax=info["scale"][-1],
                colorbar=dict(
                    title=info["label"] + (f" ({info['unit']})" if info["unit"] else ""),
                    thickness=20,
                )
            ),
            text=[
                f"{row['sitename']}<br>{info['label']}: {row[info['column']]} {info['unit']}<br>{row['status']}"
                for _, row in df.iterrows()
            ],
            hoverinfo="text",
            name=info["label"],
        ))
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=23.7, lon=121.0),
                zoom=6
            ),
            margin={"r":0,"t":50,"l":0,"b":0},
            title=f"即時空氣品質指標 ({info['label']})",
            title_font_size=18,
            title_x=0.01,
            title_y=0.98,
        )
        return fig

    return dash_app

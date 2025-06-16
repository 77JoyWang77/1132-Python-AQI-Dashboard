import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

def create_dash_aqi_24_map_app(server):
    # 讀取資料
    df = pd.read_csv("data/aqi24.csv")
    df = df.dropna(subset=['aqi'])
    df["datacreationdate"] = pd.to_datetime(df["datacreationdate"])
    df["hour"] = df["datacreationdate"].dt.strftime("%Y-%m-%d %H:%M")

    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_aqi_24_map/',
        suppress_callback_exceptions=True
    )

    dash_app.layout = html.Div([
        dcc.Graph(
            id="aqi-24-map",
            config={"scrollZoom": True},
            style={"height": "750px"}
        )
    ])

    @dash_app.callback(
        Output("aqi-24-map", "figure"),
        Input("aqi-24-map", "id")
    )
    def render_map(_):
        fig = px.scatter_mapbox(
            df,
            lat="latitude", lon="longitude",
            color="aqi", size_max=15, zoom=6,
            hover_name="sitename",
            hover_data={
                "aqi": True,
                "status": True,
                "hour": True,
                "latitude": False,
                "longitude": False,
            },
            animation_frame="hour",
            color_continuous_scale=[
                [0.0, "#00E400"], [0.1, "#FFFF00"], [0.25, "#FF7E00"],
                [0.35, "#FF0000"], [0.5, "#8F3F97"], [0.7, "#7E0023"], [1.0, "#28000B"]
            ],
            range_color=[0, 500]
        )
        fig.update_traces(marker=dict(size=13))  # 可調size
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            title="台灣 AQI 即時地圖動畫（24小時）"
        )
        return fig

    return dash_app

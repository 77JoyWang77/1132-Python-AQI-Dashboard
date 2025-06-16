from flask import Flask, render_template

server = Flask(__name__)

from dash_apps.dash_aqiyear import create_dash_aqiyear_app
aqiyear_app = create_dash_aqiyear_app(server)

from dash_apps.dash_pollutant import create_dash_pollutant_app
pollutant_app = create_dash_pollutant_app(server)

from dash_apps.dash_site import create_dash_site_app
site_app = create_dash_site_app(server)

from dash_apps.dash_month import create_dash_month_app
create_dash_month_app(server)

from dash_apps.dash_mainpollutant import create_dash_mainpollutant_app
create_dash_mainpollutant_app(server)

from dash_apps.dash_year import create_dash_year_app
create_dash_year_app(server)

from dash_apps.dash_aqi_level_pie import create_dash_aqi_level_pie_app
create_dash_aqi_level_pie_app(server)

from dash_apps.dash_pollutant_pie import create_dash_pollutant_pie_app
create_dash_pollutant_pie_app(server)

from dash_apps.dash_calendar import create_dash_calendar_app
create_dash_calendar_app(server)

from dash_apps.dash_line_daily import create_dash_line_daily_app
create_dash_line_daily_app(server)

from dash_apps.dash_aqi_online_30 import create_dash_aqi_online_30_app
create_dash_aqi_online_30_app(server)

from dash_apps.dash_aqi_online_24 import create_dash_aqi_online_24_app
create_dash_aqi_online_24_app(server)

from dash_apps.dash_aqi_map import create_dash_aqi_map_app
create_dash_aqi_map_app(server)

from dash_apps.dash_aqi_24_map import create_dash_aqi_24_map_app
create_dash_aqi_24_map_app(server)

@server.route("/")
def index():
    return render_template("index.html")   # 主頁模板

if __name__ == "__main__":
    # 啟動 Flask server
    server.run(debug=True, port=5000)

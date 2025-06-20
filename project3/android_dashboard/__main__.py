import asyncio
from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import os
from pathlib import PurePath
import time

from android_analyzer.utils import get_app_net_stats
from android_analyzer_common import select_device, start_adb
import pandas as pd
from ppadb.client_async import ClientAsync as AdbClient
import plotly.express as px

TIMEOUT = 60
NETSTATS_FILE = PurePath(os.getcwd(), "out", "app_netstats.csv")

app = Dash()
client = AdbClient(host="127.0.0.1", port=5037)
devices = []

@callback(
    Output("app-display", "children"),
    Input("adb-device-select", "value"),
    [State("app-display", "children")]
)
def update_output(value, old_display):
    global devices
    if not value:
        return no_update
    device = None
    for dev in devices:
        if dev.serial == value:
            device = dev
    if device == None:
        return no_update
    asyncio.run(get_app_net_stats(device))
    ret_val = old_display
    if os.path.exists(str(NETSTATS_FILE)):
        df = pd.read_csv(str(NETSTATS_FILE))
        ret_val[0] = dcc.Graph(
            figure=px.pie(
                df,
                values="Transmitted Data",
                names="Package",
                title="Transmitted Data by Package",
            ).update_traces(textinfo="none")
        )
        ret_val[1] = dcc.Graph(
            figure=px.pie(
                df,
                values="Received Data",
                names="Package",
                title="Received Data by Package",
            ).update_traces(textinfo="none")
        )


    return ret_val

async def main():
    global devices
    start_adb()

    # Get a list of connected devices
    dev_serials = []
    devices = await client.devices()
    for dev in devices:
        dev_serials.append(dev.serial)

    # Create a drop-down menu to select the appropriate device
    app.layout = html.Div(
        children = [
            html.Label(["Select Device Serial:"]),
            dcc.Dropdown(dev_serials, multi=False, id="adb-device-select"),
            html.Hr(),
            dcc.Loading(html.Div(id="app-display", children=[html.Div(), html.Div()]), id="loading-component"),
        ])
    app.run()

if __name__ == "__main__":
    asyncio.run(main())

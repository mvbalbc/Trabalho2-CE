import requests
import pandas as pd

API_KEY = "KEY_DA_WEBAPI_DO_STEAM"

all_games = []
last_appid = 0

while True:

    params = {
        "key": API_KEY,
        "include_games": "true",
        "include_dlc": "false",
        "include_software": "false",
        "include_videos": "false",
        "include_hardware": "false",
        "max_results": 200000,
        "last_appid": last_appid
    }

    r = requests.get(
        "https://api.steampowered.com/IStoreService/GetAppList/v1/",
        params=params,
        timeout=360
    )

    data = r.json()["response"]

    apps = data["apps"]

    all_games.extend(apps)

    if not data.get("have_more_results", False):
        break

    last_appid = data["last_appid"]

df = pd.DataFrame(all_games)

df.to_csv(
    "steam_games.csv",
    index=False,
    encoding="utf-8-sig"
)
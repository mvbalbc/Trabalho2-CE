import pandas as pd

df = pd.read_csv("steam_games.csv")

games = df.to_dict("records")

import aiohttp

async def fetch_game(session, appid):
    url = "https://store.steampowered.com/api/appdetails"

    try:

        async with session.get(
            url,
            params={"appids": appid}
        ) as resp:

            data = await resp.json()

            key = str(appid)

            if not data.get(key, {}).get("success"):
                return None

            return data[key]["data"]

    except Exception:
        return None
    
def is_indie(game_data):

    genres = game_data.get("genres", [])

    return any(
        genre["description"] == "Indie"
        for genre in genres
    )

import asyncio

SEM = asyncio.Semaphore(100)

async def process_game(session, row):

    async with SEM:

        appid = row["appid"]

        data = await fetch_game(session, appid)

        if data is None:
            return None

        if is_indie(data):

            return {
                "appid": appid,
                "name": row["name"]
            }

        return None
    
async def main(games):

    connector = aiohttp.TCPConnector(limit=100)

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        tasks = [
            process_game(session, game)
            for game in games
        ]

        results = await asyncio.gather(*tasks)

        return [
            r for r in results
            if r is not None
        ]
    
indie_games = asyncio.run(main(games))

pd.DataFrame(indie_games).to_csv(
    "steam_indie_games.csv",
    index=False,
    encoding="utf-8-sig"
)
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from json import load
from pathlib import Path
from fastapi import Response
from requests import get
from sqlite3 import connect, Connection
from time import sleep

seconds: float = 0.4  # Delay execution for a given number of seconds.


def main() -> None:
    games: dict = load_games(True, True)
    console: str
    game_list: list
    now: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    create_sql: str = Path(__file__).parent.joinpath("data/games/create.sql").read_text()
    insert_sql: str = Path(__file__).parent.joinpath("data/games/insert.sql").read_text()
    connection: Connection = connect(Path(__file__).parent.joinpath("data/apy.db"))
    connection.cursor().execute(create_sql)

    for console, game_list in games.items():
        for game in game_list:
            url: str = f"https://www.pricecharting.com/game/{console}/{game['name']}"
            response: Response = get(url)
            soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
            id: str = soup.find("h1", id="product_name").get("title")
            loose_price: Tag = soup.find("div", id="full-prices").find("td", class_="price").text.replace("$", "")
            data: dict = {"console_name": console, "id": id , "product_name": game["name"], "loose_price": loose_price, "moment": now}
            connection.cursor().executemany(insert_sql, [(data["console_name"], data["id"], data["product_name"], data["loose_price"], data["moment"])])
            sleep(seconds)

    connection.commit()
    connection.close()


def load_games(filter_owned: bool = False, sanitize: bool = False) -> dict:
    games: dict = load(open(Path(__file__).parent.joinpath("data/game.json")))

    if filter_owned:
        games = _filter_owned(games)

    if sanitize:
        games = _sanitize(games)

    return games


def _filter_owned(games: dict) -> dict:
    owned: dict = {}

    for console, game_list in games.items():
        owned[console] = [game for game in game_list if game["owned"]]

    return owned


def _sanitize(games: dict) -> dict:
    console: str
    game: dict
    sanitized: dict = {}

    for console, game in games.items():
        console = console.lower().replace(" ", "-")
        game = [{key: value.lower().replace(" ", "-") if isinstance(value, str) else value for key, value in g.items()} for g in game]
        sanitized[console] = game

    return sanitized

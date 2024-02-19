from bs4 import BeautifulSoup, Tag
from datetime import datetime
from json import load
from pathlib import Path
from fastapi import Response
from requests import get
from sqlite3 import Cursor, connect, Connection
from time import sleep

exclude_unowned: bool = True  # Exclude unowned games.
exclude_reproduction: bool = True  # Exclude game reproductions.
sanitize: bool = True  # Sanitize console and game names for PriceCharting.
verbose: bool = True  # View data during processing.
seconds: float = 0.4  # Delay execution for a given number of seconds.


def main() -> None:
    now: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    create_sql: str = Path(__file__).parent.joinpath("data/games/create.sql").read_text()
    select_all_sql: str = Path(__file__).parent.joinpath("data/games/select_all.sql").read_text()
    select_stats_sql: str = Path(__file__).parent.joinpath("data/games/select_stats.sql").read_text()
    insert_sql: str = Path(__file__).parent.joinpath("data/games/insert.sql").read_text()
    connection: Connection = connect(Path(__file__).parent.joinpath("data/apy.db"))
    connection.cursor().execute(create_sql)
    rows: list = execute(connection, select_all_sql)
    games: dict = load_games(exclude_unowned, exclude_reproduction, sanitize)
    filtered: list = filter_processed(games, rows)

    for game in filtered:
        endpoint = f"/{game['console_name']}/{game['product_name']}"
        url: str = f"https://www.pricecharting.com/game{endpoint}"
        response: Response = get(url)
        soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

        product_name: Tag = soup.find("h1", id="product_name")

        if not product_name:
            if verbose:
                print(f"{endpoint}: Not found")
            
            continue

        id: str = product_name.get("title")
        loose_price: Tag = soup.find("div", id="full-prices").find("td", class_="price").text.replace("$", "")
        data: dict = {"console_name": game['console_name'], "id": id , "product_name": game["product_name"], "loose_price": loose_price, "moment": now}
        
        if verbose:
            print(f"{endpoint}: {data}")
        
        connection.cursor().executemany(insert_sql, [(data["console_name"], data["id"], data["product_name"], data["loose_price"], data["moment"])])
        connection.commit()
        sleep(seconds)

    rows: list = execute(connection, select_stats_sql)
    connection.close()

    for row in rows:
        print(row)


def filter_processed(games: dict, rows: list) -> list:
    console: str
    products: list
    product: dict
    filtered: list = []

    for console, products in games.items():
        for product in products:
            if not any(row["console_name"] == console and row["product_name"] == product["name"] for row in rows):
                filtered.append({"console_name": console, "product_name": product["name"]})

    return filtered


def execute(connection: Connection, sql: str) -> list:
    """Run a SQL query and return its results as JSON data."""

    cursor: Cursor = connection.cursor()
    cursor.execute(sql)
    rows: list = cursor.fetchall()
    cursor.close()
    results: list = []

    if rows:
        row: tuple
        columns: list = [description[0] for description in cursor.description]

        for row in rows:
            results.append(dict(zip(columns, row)))

    return results


def load_games(exclude_unowned: bool = False, exclude_reproduction: bool = True, sanitize: bool = False) -> dict:
    """Load games from a JSON file."""

    games: dict = load(open(Path(__file__).parent.joinpath("data/game.json")))

    if exclude_unowned or exclude_reproduction:
        games = _filter(games, exclude_unowned, exclude_reproduction)

    if sanitize:
        games = _sanitize(games)

    return games


def _filter(games: dict, exclude_unowned: bool = False, exclude_reproduction: bool = False) -> dict:
    """Exclude unowned games and/or reproductions."""
    
    filtered: dict = {}

    for console, game_list in games.items():
        filtered[console] = [game for game in game_list if exclude_unowned and (not "owned" in game or game["owned"]) and exclude_reproduction and (not "reproduction" in game or not game["reproduction"])]

    return filtered


def _sanitize(games: dict) -> dict:
    """Sanitize console and game names for PriceCharting."""

    console_name: str
    product: dict
    data: dict = {}
    
    for console_name, product in games.items():
        console_name = _sanitize_string(console_name)
        product = [{key: _sanitize_string(value) if isinstance(value, str) else value for key, value in p.items()} for p in product]
        data[console_name] = product

    return data


def _sanitize_string(string: str) -> str:
    """Sanitize a string for PriceCharting."""

    return string.lower().replace("/ ", "").replace(" ", "-").replace(":", "")

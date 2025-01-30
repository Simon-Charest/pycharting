from bs4 import BeautifulSoup, Tag
from datetime import datetime
from glob import glob
from json import load
from fastapi import Response
from requests import get
from sqlite3 import Connection
from time import sleep

from constant import *
from database import execute


def crawl_price_charting(connection: Connection, console_name: str = None) -> None:
    now: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    create_sql: str = DATABASE_PATH.joinpath("games/create.sql").read_text()
    select_all_sql: str = DATABASE_PATH.joinpath("games/select_all.sql").read_text()
    insert_sql: str = DATABASE_PATH.joinpath("games/insert.sql").read_text()
    connection.cursor().execute(create_sql)
    rows: list = execute(connection, select_all_sql)
    data: dict = _load_data(console_name, EXCLUDE_UNOWNED, EXCLUDE_REPRODUCTION, SANITIZE)
    filtered: list = _filter_processed(data, rows)

    for game in filtered:
        endpoint = f"/{game['console_name']}/{game['product_name']}"
        url: str = f"https://www.pricecharting.com/game{endpoint}"
        response: Response = get(url)
        soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
        product_name: Tag = soup.find("h1", id="product_name")

        if not product_name:
            if VERBOSE:
                print(f"{endpoint}: Not found")
            
            continue

        id: str = product_name.get("title")
        loose_price: Tag = soup.find("div", id="full-prices").find("td", class_="price").text.replace("$", "")
        data: dict = {"console_name": game['console_name'], "id": id , "product_name": game["product_name"], "loose_price": loose_price, "moment": now}
        
        if VERBOSE:
            print(f"{endpoint}: {data}")
        
        connection.cursor().executemany(insert_sql, [(data["console_name"], data["id"], data["product_name"], data["loose_price"], data["moment"])])
        connection.commit()
        sleep(SECONDS)


def _load_data(title: str = None, EXCLUDE_UNOWNED: bool = False, EXCLUDE_REPRODUCTION: bool = True, SANITIZE: bool = False) -> dict:
    """Load data from a JSON file."""

    # Get all JSON files in the directory
    paths: list = glob(str(DATA_PATH))
    
    path: str
    data: dict = {}

    # Loop through each JSON file
    for path in paths:
        # Read and load the JSON data from the file
        data.update(load(open(path)))

    if title and title != "*":
        data = {title: data.get(title, [])}

    if EXCLUDE_UNOWNED or EXCLUDE_REPRODUCTION:
        data = _filter(data, EXCLUDE_UNOWNED, EXCLUDE_REPRODUCTION)

    if SANITIZE:
        data = _sanitize(data)

    return data


def _filter(data: dict, EXCLUDE_UNOWNED: bool = False, EXCLUDE_REPRODUCTION: bool = False) -> dict:
    """Exclude unowned and/or reproductions."""
    
    group: str
    titles: list
    filtered: dict = {}

    for group, titles in data.items():
        filtered[group] = [
            game for game in titles if
            EXCLUDE_UNOWNED and (not "owned" in game or game["owned"])
            and EXCLUDE_REPRODUCTION and (not "reproduction" in game or not game["reproduction"])
            and EXCLUDE_REPRODUCTION and (not "virtual" in game or not game["virtual"])
        ]

    return filtered


def _sanitize(data: dict) -> dict:
    """Sanitize console and game names for PriceCharting."""

    console_name: str
    product: dict
    sanitized: dict = {}
    
    for console_name, product in data.items():
        console_name = _sanitize_string(console_name)
        product = [{key: _sanitize_string(value) if isinstance(value, str) else value for key, value in p.items()} for p in product]
        sanitized[console_name] = product

    return sanitized


def _sanitize_string(string: str, olds: list[tuple] = [("/ ", ""), (" ", "-"), (".", ""), (":", "")]) -> str:
    """Sanitize a string for PriceCharting."""

    old: tuple

    for old in olds:
        string = string.replace(old[0], old[1])

    return string.lower()


def _filter_processed(data: dict, rows: list) -> list:
    console: str
    products: list
    product: dict
    filtered: list = []

    for console, products in data.items():
        for product in products:
            if not any(row["console_name"] == console and row["product_name"] == product["name"] for row in rows):
                filtered.append({"console_name": console, "product_name": product["name"]})

    return filtered

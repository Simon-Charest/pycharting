from bs4 import BeautifulSoup, Tag
from datetime import datetime
from glob import glob
from json import load
from fastapi import Response
from pathlib import Path
from requests import get
from sqlite3 import Cursor, Connection
from time import sleep

# APy
from constant import *


def crawl_price_charting(connection: Connection, console_name: str = None) -> None:
    now: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    create_sql: str = Path(__file__).parent.joinpath("data/games/create.sql").read_text()
    select_all_sql: str = Path(__file__).parent.joinpath("data/games/select_all.sql").read_text()
    insert_sql: str = Path(__file__).parent.joinpath("data/games/insert.sql").read_text()
    connection.cursor().execute(create_sql)
    rows: list = _execute(connection, select_all_sql)
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


def print_statistical_report(connection: Connection) -> None:
    # Get data
    sql: str = Path(__file__).parent.joinpath("data/games/select_stats.sql").read_text()
    rows: list = _execute(connection, sql)

    # Calculate totals
    row: dict
    count: int = 0
    min: float = 0
    max: float = 0
    sum: float = 0
    
    for row in rows:
        count += row["count"]

        if min == 0 or row["min"] < min:
            min = row["min"]

        if row["max"] > max:
            max = row["max"]

        sum += row["sum"]

    avg: float = round(sum / count, 2)

    # Append totals
    rows.append({"console_name": "total", "count": count, "min": min, "avg": avg, "max": max, "sum": sum})

    # Print data
    for row in rows:
        print(row)


def print_top_report(connection: Connection, top: str) -> None:
    # Get data
    sql: str = Path(__file__).parent.joinpath("data/games/select_top.sql").read_text()
    rows: list = _execute(connection, sql.replace("?", top))

    # Calculate totals
    row: dict
    count: int = 0
    min: float = 0
    max: float = 0
    sum: float = 0
    
    for row in rows:
        count += 1

        if min == 0 or row["loose_price"] < min:
            min = row["loose_price"]

        if row["loose_price"] > max:
            max = row["loose_price"]

        sum += row["loose_price"]

    avg: float = round(sum / count, 2)
    sum = round(sum, 2)

    # Append totals
    rows.append({"console_name": "total", "count": count, "min": min, "avg": avg, "max": max, "sum": sum})

    # Print data
    for row in rows:
        print(row)


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


def _execute(connection: Connection, sql: str) -> list:
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


def _load_data(title: str = None, EXCLUDE_UNOWNED: bool = False, EXCLUDE_REPRODUCTION: bool = True, SANITIZE: bool = False) -> dict:
    """Load data from a JSON file."""

    data: dict = {}

    # Get all JSON files in the directory
    paths: list = glob(str(Path(__file__).parent.joinpath("data/*.json")))

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


def _sanitize_string(string: str, olds: list[tuple] = [("*", "-"), ("/ ", ""), (" ", "-"), (".", ""), (":", "")]) -> str:
    """Sanitize a string for PriceCharting."""

    old: tuple

    for old in olds:
        string = string.replace(old[0], old[1])

    return string.lower()

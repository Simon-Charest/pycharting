from bs4 import BeautifulSoup, Tag
from requests import Response, get
from typing import Any


def convert_usd_cad(rows: list[dict], usd_cad_rate: float, included_keys: list[str] = None, excluded_keys: list[str] = None) -> list:
    row: dict
    key: str
    value: Any

    for row in rows:
        for key, value in row.items():
            if key in included_keys and key not in excluded_keys and isinstance(value, (int, float)):
                row[key] = round(usd_cad_rate * value, 2)
    
    return rows


def get_usd_cad_rate(url: str = "https://www.google.com/finance/quote/USD-CAD") -> float:
    response: Response = get(url)
    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    rate_element: Tag = soup.find("div", class_="YMlKec fxKbKc")

    return float(rate_element.text.strip())


def print_list(list_: list) -> None:
    item: Any
    
    for item in list_:
        print(item)

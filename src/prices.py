from bs4 import BeautifulSoup, Tag
from datetime import date
from requests import RequestException, Response, get
from urllib.parse import quote

from src.constant import REQUEST_TIMEOUT


SEARCH_URL: str = "https://www.pricecharting.com/search-products?type=prices&q="
# The Bank of Canada's official rate for the last business day. PriceCharting's pages are always in USD:
# its currency menu only converts them in the browser.
RATE_URL: str = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=1"
HEADERS: dict = {"User-Agent": "PyCharting"}
# PriceCharting's price for each part of an entry
PART_LABELS: dict = {"game": "Loose", "manual": "Manual Only", "box": "Box Only"}


class PriceChartingError(Exception):
    """PriceCharting could not be reached."""


class ProductNotFound(Exception):
    """No PriceCharting product matches the entry."""


class ExchangeRateError(Exception):
    """The USD to CAD rate could not be found."""


_rates: dict = {}  # Today's rate, so that updating many entries asks for it once


def usd_cad_rate() -> float:
    today: date = date.today()

    if today not in _rates:
        try:
            response: Response = get(RATE_URL, timeout=REQUEST_TIMEOUT, headers=HEADERS)
            response.raise_for_status()
            _rates.clear()
            _rates[today] = float(response.json()["observations"][-1]["FXUSDCAD"]["v"])
        except (RequestException, KeyError, IndexError, TypeError, ValueError) as error:
            raise ExchangeRateError() from error

    return _rates[today]


def search_query(title: str, console: str, region: str | None) -> str:
    return f"{title} {'PAL ' if region == 'PAL' else ''}{console}"


def fetch_prices(url: str | None, title: str, console: str, region: str | None) -> dict:
    """Return the product's URL and its price for every part, in CAD; a part without a price is None."""

    soup, url = _product_page(url, title, console, region)
    table: Tag | None = soup.find(id="full-prices")

    if table is None:
        raise ProductNotFound()

    prices: dict = {}

    for row in table.select("tr"):
        cells: list = [cell.get_text(strip=True) for cell in row.select("td")]

        if len(cells) >= 2:
            prices[cells[0]] = _price(cells[1])

    rate: float = usd_cad_rate()

    return {"url": url, **{key: _cad(prices.get(label), rate) for key, label in PART_LABELS.items()}}


def _cad(usd: float | None, rate: float) -> float | None:
    return None if usd is None else round(usd * rate, 2)


def _product_page(url: str | None, title: str, console: str, region: str | None) -> tuple[BeautifulSoup, str]:
    """The stored link when it is one, otherwise the search result with exactly that title."""

    if url and url.lower().startswith(("http://", "https://")):
        response: Response = _get(url)

        return BeautifulSoup(response.text, "html.parser"), response.url

    response = _get(SEARCH_URL + quote(search_query(title, console, region)))
    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

    # A single match sends the search straight to the product
    if soup.find(id="full-prices") is not None:
        return soup, response.url

    for link in soup.select("table#games_table td.title a"):
        if link.get_text(strip=True).casefold() == title.strip().casefold() and link.get("href"):
            response = _get(link["href"])

            return BeautifulSoup(response.text, "html.parser"), response.url

    raise ProductNotFound()


def _get(url: str) -> Response:
    try:
        response: Response = get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
    except RequestException as error:
        raise PriceChartingError() from error

    if response.status_code == 404:
        raise ProductNotFound()

    if not response.ok:
        raise PriceChartingError()

    return response


def _price(text: str) -> float | None:
    """'$1,234.50' as a number; PriceCharting shows a dash or N/A when it has no price."""

    try:
        return float(text.replace("$", "").replace(",", ""))
    except ValueError:
        return None

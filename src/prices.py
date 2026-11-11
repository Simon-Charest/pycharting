import re
from bs4 import BeautifulSoup, Tag
from datetime import date
from requests import RequestException, Response, get
from threading import Lock
from time import monotonic, sleep
from unicodedata import normalize
from urllib.parse import quote, unquote

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


class RateLimited(Exception):
    """PriceCharting refuses requests for now (HTTP 429): wait before asking again."""


_rates: dict = {}  # Today's rate, so that updating many entries asks for it once

# Going easy on PriceCharting, so as not to be banned: one request at a time, at least MIN_INTERVAL apart
MIN_INTERVAL: float = 2.0  # Seconds between two PriceCharting requests, whoever asks
DEFAULT_RETRY_WAIT: float = 30.0  # When a 429 does not say how long to wait
MAX_RETRY_WAIT: float = 60.0  # Longer than that, give up instead of keeping a request waiting
PAUSE_AFTER_REFUSAL: float = 600.0  # After a second 429, nothing is asked of PriceCharting for at least that long
_lock: Lock = Lock()
_last_request: float = float("-inf")
_paused_until: float = float("-inf")


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


# PriceCharting's console, as in its links (/game/<console>/<title>), for each system name the collection uses
CONSOLE_SLUGS: dict = {
    "3ds": "nintendo-3ds",
    "nintendo 3ds": "nintendo-3ds",
    "atari 2600": "atari-2600",
    "atari 7800": "atari-7800",
    "colecovision": "colecovision",
    "commodore 64": "commodore-64",
    "ds": "nintendo-ds",
    "nintendo ds": "nintendo-ds",
    "gba": "gameboy-advance",
    "gameboy advance": "gameboy-advance",
    "game boy advance": "gameboy-advance",
    "gameboy": "gameboy",
    "game boy": "gameboy",
    "gameboy color": "gameboy-color",
    "game boy color": "gameboy-color",
    "nintendo game boy color": "gameboy-color",
    "gamecube": "gamecube",
    "intellivision": "intellivision",
    "n64": "nintendo-64",
    "nintendo 64": "nintendo-64",
    "nes": "nes",
    "nintendo game & watch": "game-&-watch",
    "switch": "nintendo-switch",
    "nintendo switch": "nintendo-switch",
    "pc": "pc-games",
    "playstation": "playstation",
    "playstation 2": "playstation-2",
    "playstation 3": "playstation-3",
    "playstation 4": "playstation-4",
    "playstation 5": "playstation-5",
    "playstation vita": "playstation-vita",
    "psp": "psp",
    "snes": "super-nintendo",
    "super nintendo": "super-nintendo",
    "sega genesis": "sega-genesis",
    "sega master system": "sega-master-system",
    "ti-99": "ti-99",
    "wii": "wii",
    "wii u": "wii-u",
    "xbox 360": "xbox-360",
}
# Systems whose name already says the standard, whatever the entry's: the Super Famicom is Japanese, and the
# Mega Drive here is European (in North America, it is the Genesis)
FIXED_SLUGS: dict = {"super famicom": "super-famicom", "sega mega drive": "pal-sega-mega-drive"}
# PriceCharting files the European Genesis under its European name
PAL_SLUGS: dict = {"sega-genesis": "pal-sega-mega-drive"}
# Every console above, in every standard: a stored link to anything else (an amiibo, an Amiga game, a strategy guide)
# is a deliberate choice, and is kept
KNOWN_SLUGS: set = {prefix + slug for slug in [*CONSOLE_SLUGS.values(), *FIXED_SLUGS.values()] for prefix in ("", "pal-", "jp-")}


def console_slug(console: str, region: str | None) -> str | None:
    """PriceCharting's console for that system and standard (NTSC when unknown), or None for a system it does not know."""

    name: str = console.strip().casefold()

    if name in FIXED_SLUGS:
        return FIXED_SLUGS[name]

    if name not in CONSOLE_SLUGS:
        return None

    slug: str = CONSOLE_SLUGS[name]

    return PAL_SLUGS.get(slug, "pal-" + slug) if region == "PAL" else slug


def search_query(title: str, console: str, region: str | None) -> str:
    slug: str | None = console_slug(console, region)

    # PriceCharting's own console name finds its products best; "pal-super-nintendo" reads "pal super nintendo"
    return f"{title} {slug.replace('-', ' ') if slug else ('PAL ' if region == 'PAL' else '') + console}"


def fetch_prices(url: str | None, title: str, console: str, region: str | None, owned: tuple = ()) -> dict:
    """Return the product's URL and its price for every part, in CAD; a part without a price is None.

    When the product is not found in the entry's standard, or has no price there for one of the owned parts,
    the other standard (NTSC or PAL) is tried: what it has fills in what is missing. The link stays the one of
    the entry's standard whenever that product exists.
    """

    try:
        prices: dict | None = _fetch_standard(url, title, console, region)
    except ProductNotFound:
        prices = None

    missing: list = list(owned) if prices is None else [part for part in owned if prices[part] is None]
    other: str | None = other_standard(console, region)

    if missing and other is not None:
        try:
            fallback: dict | None = _fetch_standard(url if prices is None else prices["url"], title, console, other)
        except ProductNotFound:
            fallback = None

        if fallback is not None:
            if prices is None:
                prices = fallback
            else:
                prices.update({part: fallback[part] for part in missing if fallback[part] is not None})

    if prices is None:
        raise ProductNotFound()

    return prices


def other_standard(console: str, region: str | None) -> str | None:
    """PAL for NTSC or an unknown standard, NTSC for PAL; None for a system that names its standard, or that PriceCharting does not know."""

    if console.strip().casefold() in FIXED_SLUGS or console_slug(console, region) is None:
        return None

    return "NTSC" if region == "PAL" else "PAL"


def _fetch_standard(url: str | None, title: str, console: str, region: str | None) -> dict:
    """The product's URL and prices in that one standard."""

    slug: str | None = console_slug(console, region)
    # An entry without a standard keeps a stored link for any standard of its system; a search looks for NTSC
    stored_slugs: set | None = None if slug is None else {slug} if region in ("NTSC", "PAL") or console.strip().casefold() in FIXED_SLUGS else {slug, console_slug(console, "PAL"), "jp-" + slug}
    soup, url = _product_page(url, title, slug, stored_slugs, search_query(title, console, region))
    url = url.split("?")[0]  # A search that leads straight to the product leaves its query on the link
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


def _product_page(url: str | None, title: str, slug: str | None, stored_slugs: set | None, query: str) -> tuple[BeautifulSoup, str]:
    """The stored link, unless it is for another system or standard; otherwise the search result with that title,
    for that system and standard."""

    if url and url.lower().startswith(("http://", "https://")):
        if _matches(url, stored_slugs) or not _matches(url, KNOWN_SLUGS):
            response: Response = _get(url)

            return BeautifulSoup(response.text, "html.parser"), response.url

        # A link for another standard or system: PriceCharting usually names the product the same way there
        # (/game/nes/duck-tales -> /game/pal-nes/duck-tales); an unknown product leads to its search page instead
        if slug is not None:
            try:
                response = _get(re.sub(r"/game/[^/]+/", f"/game/{slug}/", url, count=1))
            except ProductNotFound:
                response = None

            if response is not None and _matches(response.url, {slug}):
                soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

                if soup.find(id="full-prices") is not None:
                    return soup, response.url

    response = _get(SEARCH_URL + quote(query))
    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

    # A single match sends the search straight to the product
    if soup.find(id="full-prices") is not None:
        if not _matches(response.url, None if slug is None else {slug}):
            raise ProductNotFound()

        return soup, response.url

    # Same title, ignoring case, accents and punctuation; then the same without a variant in brackets ("[Yellow Box]")
    links: list = [link for link in soup.select("table#games_table td.title a") if link.get("href") and _matches(link["href"], None if slug is None else {slug})]
    wanted: str = _comparable(title)

    for comparable in (_comparable, lambda text: _comparable(re.sub(r"\[.*?\]", "", text))):
        for link in links:
            if comparable(link.get_text(strip=True)) == wanted:
                response = _get(link["href"])

                return BeautifulSoup(response.text, "html.parser"), response.url

    raise ProductNotFound()


def _matches(url: str, slugs: set | None) -> bool:
    """Whether a PriceCharting product link is for that console; any link will do for a system PriceCharting does not know."""

    if slugs is None:
        return True

    match: re.Match | None = re.search(r"/game/([^/]+)/", url)

    return match is not None and unquote(match.group(1)).casefold() in slugs


def _comparable(title: str) -> str:
    """'The Legend of Zelda: Link's Awakening' and 'Legend of Zelda Links Awakening' read the same; so do é and e, & and and."""

    text: str = normalize("NFD", title).encode("ascii", "ignore").decode().casefold().replace("&", " and ")
    text = re.sub(r"[^a-z0-9 ]+", "", text.replace("-", " "))
    text = " ".join(text.split())

    return text.removeprefix("the ")


def _get(url: str) -> Response:
    """A PriceCharting page, never sooner than MIN_INTERVAL after the previous one.

    When PriceCharting says there are too many requests (429), wait as long as it asks, if that is reasonable, and
    try once more; if it refuses again, ask it nothing more for a while, so that the site is never hammered.
    """

    global _paused_until

    for attempt in range(2):
        with _lock:
            if monotonic() < _paused_until:
                raise RateLimited()

            wait: float = _last_request + MIN_INTERVAL - monotonic()

            if wait > 0:
                sleep(wait)

            try:
                response: Response = get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)
            except RequestException as error:
                raise PriceChartingError() from error
            finally:
                _mark_request()

            if response.status_code != 429:
                break

            delay: float = _retry_after(response)

            if attempt or delay > MAX_RETRY_WAIT:
                _paused_until = monotonic() + max(delay, PAUSE_AFTER_REFUSAL)

                raise RateLimited()

            sleep(delay)

    if response.status_code == 404:
        raise ProductNotFound()

    if not response.ok:
        raise PriceChartingError()

    return response


def _mark_request() -> None:
    global _last_request
    _last_request = monotonic()


def _retry_after(response: Response) -> float:
    """PriceCharting's Retry-After, in seconds; a date or nothing counts as the default."""

    try:
        return max(float(response.headers.get("Retry-After", "")), 0.0)
    except ValueError:
        return DEFAULT_RETRY_WAIT


def _price(text: str) -> float | None:
    """'$1,234.50' as a number; PriceCharting shows a dash or N/A when it has no price."""

    try:
        return float(text.replace("$", "").replace(",", ""))
    except ValueError:
        return None

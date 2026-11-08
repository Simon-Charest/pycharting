from datetime import date
from fastapi import FastAPI, HTTPException, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlcipher3.dbapi2 import Connection
from typing import Annotated, Any, Literal
from uvicorn import run

try:
    from constant import API_HOST, API_PORT, API_RELOAD
    from database import add_collection_item as add_item, change_collection_entry, ensure_collection_schema, get_collection_entries, get_entry_prices, get_owners, open_database
    from prices import ExchangeRateError, PriceChartingError, ProductNotFound, fetch_prices
except ImportError:
    from pycharting.constant import API_HOST, API_PORT, API_RELOAD
    from pycharting.database import add_collection_item as add_item, change_collection_entry, ensure_collection_schema, get_collection_entries, get_entry_prices, get_owners, open_database
    from pycharting.prices import ExchangeRateError, PriceChartingError, ProductNotFound, fetch_prices


class RevalidatedStaticFiles(StaticFiles):
    """Static files that browsers must check for changes before reusing their copy."""

    async def get_response(self, path: str, scope: Any) -> Response:
        response: Response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"

        return response


origin_port: str = "" if API_PORT == 80 else f":{API_PORT}"  # Browsers omit the default port from their origin.
app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{API_HOST}{origin_port}", f"http://localhost{origin_port}"],  # Other sites must not reach the collection.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/static", RevalidatedStaticFiles(directory=Path(__file__).parent.joinpath("ui/static")), name="static")
connection: Connection = open_database()
ensure_collection_schema(connection)

RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Cell = float | int | str | None
IsoDate = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^\d{4}-\d{2}-\d{2}$")]  # yyyy-mm-dd


class CollectionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_name: RequiredText
    name: RequiredText
    region: Literal["NTSC", "PAL"] | None = None
    owner_id: int | None = None
    source: RequiredText | None = None
    console: bool | None = None
    gamepad: bool | None = None
    amiibo: bool | None = None
    accessory: bool | None = None
    wishlist: bool | None = None
    previously_owned: bool | None = None
    quantity: int = Field(default=1, ge=0)
    reproduction: bool | None = None
    virtual: bool | None = None
    game: Cell = None
    manual: Cell = None
    box: Cell = None
    date: IsoDate | None = None
    paid: Cell = None
    pricecharting: str | None = None


class NewCollectionItem(CollectionItem):
    owner_id: int


class SpreadsheetRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    system: RequiredText
    title: RequiredText
    region: Literal["NTSC", "PAL"] | None = None
    owner_id: int | None = None
    source: RequiredText | None = None
    console: bool | None = None
    amiibo: bool | None = None
    accessory: bool | None = None
    wishlist: bool | None = None
    gamepad: bool | None = None
    previously_owned: bool | None = None
    reproduction: bool | None = None
    virtual: bool | None = None
    game: Cell = None
    box: Cell = None
    manual: Cell = None
    date: IsoDate | None = None
    paid: Cell = None
    pricecharting: str | None = None
    quantity: int = Field(default=1, ge=0)


def run_api() -> None:
    run(f"{__name__}:app", host=API_HOST, port=API_PORT, reload=API_RELOAD)


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(Path(__file__).parent.joinpath("ui/collection.html"), media_type="text/html", headers={"Cache-Control": "no-cache"})


@app.get("/collection/entries")
async def collection_entries() -> list:
    return get_collection_entries(connection)


@app.get("/collection/owners")
async def collection_owners() -> list:
    return get_owners(connection)


@app.post("/collection/items", status_code=201)
async def add_collection_item(item: NewCollectionItem) -> dict:
    if not add_item(connection, item.model_dump()):
        raise HTTPException(status_code=404, detail="Owner not found.")

    return {"message": "OK"}


@app.put("/collection/items/{id}")
async def update_collection_item(id: int, item: CollectionItem) -> dict:
    return _change_entry("update_item", {**item.model_dump(), "id": id})


@app.delete("/collection/items/{id}")
async def delete_collection_item(id: int) -> dict:
    return _change_entry("delete_item", {"id": id})


@app.put("/collection/rows/{id}")
async def update_collection_row(id: int, row: SpreadsheetRow) -> dict:
    return _change_entry("update_row", {**row.model_dump(), "id": id})


@app.delete("/collection/rows/{id}")
async def delete_collection_row(id: int) -> dict:
    return _change_entry("delete_row", {"id": id})


def _change_entry(script: str, parameters: dict) -> dict:
    if not change_collection_entry(connection, script, parameters):
        raise HTTPException(status_code=404, detail="Entry not found.")

    return {"message": "OK"}


@app.get("/health")
async def health() -> dict:
    return {"message": "The state of the service is healthy."}


@app.post("/collection/{kind}/{id}/prices")
async def update_entry_prices(kind: Literal["items", "rows"], id: int) -> dict:
    """Refresh Item, Manual and Box from PriceCharting, in CAD, and date them today.

    Only the parts that are owned, that is that have a value, are refreshed: an empty part stays empty.
    """

    singular: str = kind[:-1]
    entry: dict | None = get_entry_prices(connection, singular, id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found.")

    owned: list = [part for part in ("game", "manual", "box") if entry[part] is not None and entry[part] != ""]

    if not owned:
        raise HTTPException(status_code=409, detail="nothing_owned")

    try:
        prices: dict = await run_in_threadpool(fetch_prices, entry["pricecharting"], entry["title"], entry["console"], entry["region"])
    except ProductNotFound:
        raise HTTPException(status_code=409, detail="product_not_found")
    except PriceChartingError:
        raise HTTPException(status_code=502, detail="pricecharting")
    except ExchangeRateError:
        raise HTTPException(status_code=502, detail="exchange_rate")

    # A part PriceCharting has no price for keeps the value it had
    values: dict = {part: prices[part] if part in owned and prices[part] is not None else entry[part] for part in ("game", "manual", "box")}
    values.update({"date": date.today().isoformat(), "pricecharting": prices["url"], "id": id})
    change_collection_entry(connection, f"update_{singular}_prices", values)

    return values

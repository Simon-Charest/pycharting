from fastapi import FastAPI, HTTPException, Response
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
    from database import add_collection_item as add_item, change_collection_entry, ensure_collection_schema, get_collection_entries, get_owners, open_database
except ImportError:
    from pycharting.constant import API_HOST, API_PORT, API_RELOAD
    from pycharting.database import add_collection_item as add_item, change_collection_entry, ensure_collection_schema, get_collection_entries, get_owners, open_database


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
    wishlist: bool | None = None
    previously_owned: bool | None = None
    quantity: int = Field(default=1, ge=0)
    reproduction: bool | None = None
    virtual: bool | None = None
    game: Cell = None
    manual: Cell = None
    box: Cell = None
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
    wishlist: bool | None = None
    gamepad: bool | None = None
    previously_owned: bool | None = None
    reproduction: bool | None = None
    virtual: bool | None = None
    game: Cell = None
    box: Cell = None
    manual: Cell = None
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

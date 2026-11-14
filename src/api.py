from datetime import date
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlcipher3.dbapi2 import Connection
from typing import Annotated, Any, Literal
from uvicorn import run

from src.auth import ADMINISTRATOR, ROLES, SESSION_COOKIE, SESSION_DAYS, NameTaken, SelfChange, create_account, delete_account, is_locked, list_accounts, session_user, sign_in, sign_out, update_account
from src.constant import API_HOST, API_ORIGINS, API_PORT, API_RELOAD, UI_PATH
from src.database import add_collection_item as add_item, change_collection_entry, ensure_collection_schema, get_collection_entries, get_entry_prices, get_owners, open_database
from src.prices import ExchangeRateError, PriceChartingError, ProductNotFound, RateLimited, fetch_prices


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
    allow_origins=[f"http://{API_HOST}{origin_port}", f"http://localhost{origin_port}", *API_ORIGINS],  # Other sites must not reach the collection.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/static", RevalidatedStaticFiles(directory=UI_PATH), name="static")
connection: Connection = open_database()
ensure_collection_schema(connection)

# Everything else needs a signed-in account: the rest of the collection, its Web API and the API's documentation
PUBLIC_PATHS: tuple = ("/login", "/auth/", "/static/", "/health")
VISITOR_PATHS: tuple = ("/", "/collection/entries")  # Matched whole: what anyone may read without an account
READ_METHODS: tuple = ("GET", "HEAD", "OPTIONS")
API_PATHS: tuple = ("/collection/", "/accounts")  # Answer with an error the page can read, rather than a redirect
ADMINISTRATOR_PATHS: tuple = ("/users", "/accounts")  # The Users page and its Web API


@app.middleware("http")
async def require_sign_in(request: Request, call_next: Any) -> Response:
    if request.url.path.startswith(PUBLIC_PATHS):
        return await call_next(request)

    user: dict | None = session_user(connection, request.cookies.get(SESSION_COOKIE))

    if user is None:
        # The collection page is open to all, showing only what is for sale; a visitor is no one, hence None
        if request.method in READ_METHODS and request.url.path in VISITOR_PATHS:
            request.state.user = None

            return await call_next(request)

        # The page goes to the sign-in form; the Web API answers, so that the page can send it there too
        if request.url.path.startswith(API_PATHS):
            return JSONResponse({"detail": "not_signed_in"}, status_code=401)

        return RedirectResponse("/login", status_code=303)

    # Collaborators can only look: adding, editing, deleting and updating prices are for administrators,
    # and so is anything about the accounts, even looking at them
    if (request.method not in READ_METHODS or request.url.path.startswith(ADMINISTRATOR_PATHS)) and user["role"] != ADMINISTRATOR:
        # A collaborator who opens the Users page lands back on Home
        if not request.url.path.startswith(API_PATHS):
            return RedirectResponse("/", status_code=303)

        return JSONResponse({"detail": "read_only"}, status_code=403)

    request.state.user = user

    return await call_next(request)

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
    damaged: bool | None = None
    selling: bool | None = None
    buying: bool | None = None
    reserved: bool | None = None
    sold: bool | None = None
    wishlist: bool | None = None
    previously_owned: bool | None = None
    quantity: int = Field(default=1, ge=0)
    reproduction: bool | None = None
    virtual: bool | None = None
    game: Cell = None
    manual: Cell = None
    box: Cell = None
    complete: Cell = None
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
    damaged: bool | None = None
    selling: bool | None = None
    buying: bool | None = None
    reserved: bool | None = None
    sold: bool | None = None
    wishlist: bool | None = None
    gamepad: bool | None = None
    previously_owned: bool | None = None
    reproduction: bool | None = None
    virtual: bool | None = None
    game: Cell = None
    box: Cell = None
    manual: Cell = None
    complete: Cell = None
    date: IsoDate | None = None
    paid: Cell = None
    pricecharting: str | None = None
    quantity: int = Field(default=1, ge=0)


def run_api() -> None:
    run(f"{__name__}:app", host=API_HOST, port=API_PORT, reload=API_RELOAD)


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(UI_PATH.joinpath("collection.html"), media_type="text/html", headers={"Cache-Control": "no-cache"})


@app.get("/login", response_model=None)
async def login_page(request: Request) -> FileResponse | RedirectResponse:
    """The sign-in page, reached from the collection; someone already signed in is sent back to it."""

    if session_user(connection, request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse("/", status_code=303)

    return FileResponse(UI_PATH.joinpath("login.html"), media_type="text/html", headers={"Cache-Control": "no-cache"})


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: RequiredText
    password: Annotated[str, StringConstraints(min_length=1, max_length=1024)]


@app.post("/auth/login")
async def login(credentials: Credentials, request: Request, response: Response) -> dict:
    if is_locked(credentials.username):
        raise HTTPException(status_code=429, detail="too_many_attempts")

    # Not in a thread pool: the database connection is only ever used from the event loop
    token: str | None = sign_in(connection, credentials.username, credentials.password)

    if token is None:
        raise HTTPException(status_code=401, detail="invalid_credentials")

    # Behind NGINX, the browser's connection is HTTPS even though NGINX reaches the app over HTTP
    secure: bool = request.headers.get("x-forwarded-proto", request.url.scheme) == "https"
    response.set_cookie(SESSION_COOKIE, token, max_age=SESSION_DAYS * 24 * 60 * 60, httponly=True, secure=secure, samesite="lax")

    return {"message": "OK"}


@app.post("/auth/logout")
async def logout(request: Request, response: Response) -> dict:
    sign_out(connection, request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(SESSION_COOKIE)

    return {"message": "OK"}


@app.get("/auth/me")
async def me(request: Request) -> dict:
    user: dict | None = session_user(connection, request.cookies.get(SESSION_COOKIE))

    if user is None:
        raise HTTPException(status_code=401, detail="not_signed_in")

    return user


@app.get("/collection/entries")
async def collection_entries(request: Request) -> list:
    entries: list = get_collection_entries(connection)
    user: dict | None = request.state.user

    # A visitor with no account sees what is for sale, and nothing else: not what it was paid, and not whose
    # it is either. Those names are left out of the answer, not merely hidden on the page.
    if user is None:
        return [
            {**entry, "owner": None, "source": None, "values": {**entry["values"], "paid": None, "owner_id": None}}
            for entry in entries if entry["values"].get("selling")
        ]

    return entries


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
    """Refresh Complete, Item, Box and Manual from PriceCharting, in CAD, and date them today.

    Only the cells that already have a value are refreshed: an empty cell is never filled in. There must be at
    least one price to refresh.
    """

    singular: str = kind[:-1]
    entry: dict | None = get_entry_prices(connection, singular, id)

    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found.")

    owned: list = [part for part in ("game", "manual", "box") if entry[part] is not None and entry[part] != ""]
    has_complete: bool = entry["complete"] is not None and entry["complete"] != ""

    if not owned and not has_complete:
        raise HTTPException(status_code=409, detail="nothing_owned")

    try:
        # An owned part without a price in the entry's standard takes the other standard's
        prices: dict = await run_in_threadpool(fetch_prices, entry["pricecharting"], entry["title"], entry["console"], entry["region"], tuple(owned), {part: entry[part] for part in ("manual", "box")})
    except ProductNotFound:
        raise HTTPException(status_code=409, detail="product_not_found")
    except RateLimited:
        raise HTTPException(status_code=429, detail="rate_limited")
    except PriceChartingError:
        raise HTTPException(status_code=502, detail="pricecharting")
    except ExchangeRateError:
        raise HTTPException(status_code=502, detail="exchange_rate")

    # Only a cell that already has a value is refreshed; an empty cell is never filled in. This holds for Complete too:
    # it is refreshed when the entry already has one, but a PriceCharting update never adds a Complete price on its own.
    values: dict = {part: prices[part] if part in owned and prices[part] is not None else entry[part] for part in ("game", "manual", "box")}
    values["complete"] = prices["complete"] if has_complete and prices["complete"] is not None else entry["complete"]
    values.update({"date": date.today().isoformat(), "pricecharting": prices["url"], "id": id})
    change_collection_entry(connection, f"update_{singular}_prices", values)

    return values


Password = Annotated[str, StringConstraints(min_length=8, max_length=1024)]
Role = Literal["administrator", "collaborator"]


PersonName = Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]


class NewAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: RequiredText
    first_name: PersonName | None = None
    last_name: PersonName | None = None
    role: Role
    password: Password


class AccountChange(BaseModel):
    """A missing name, role or password keeps the one the account has; names change only when both are given."""

    model_config = ConfigDict(extra="forbid")

    username: RequiredText | None = None
    first_name: PersonName | None = None
    last_name: PersonName | None = None
    role: Role | None = None
    password: Password | None = None


@app.get("/users")
async def users_page() -> FileResponse:
    """The Users page, for administrators."""

    return FileResponse(UI_PATH.joinpath("users.html"), media_type="text/html", headers={"Cache-Control": "no-cache"})


@app.get("/accounts")
async def users() -> list:
    return list_accounts(connection)


@app.post("/accounts", status_code=201)
async def add_user(account: NewAccount) -> dict:
    if not create_account(connection, account.username, account.password, account.role, account.first_name, account.last_name):
        raise HTTPException(status_code=409, detail="user_exists")

    return {"message": "OK"}


@app.put("/accounts/{id}")
async def update_user(id: int, change: AccountChange, request: Request) -> dict:
    try:
        names: tuple | None = (change.first_name, change.last_name) if {"first_name", "last_name"} & change.model_fields_set else None
        found: bool = update_account(connection, request.state.user["id"], id, change.role, change.password, names, change.username)
    except SelfChange:
        raise HTTPException(status_code=409, detail="self")
    except NameTaken:
        raise HTTPException(status_code=409, detail="user_exists")

    if not found:
        raise HTTPException(status_code=404, detail="Account not found.")

    return {"message": "OK"}


@app.delete("/accounts/{id}")
async def delete_user(id: int, request: Request) -> dict:
    try:
        found: bool = delete_account(connection, request.state.user["id"], id)
    except SelfChange:
        raise HTTPException(status_code=409, detail="self")

    if not found:
        raise HTTPException(status_code=404, detail="Account not found.")

    return {"message": "OK"}

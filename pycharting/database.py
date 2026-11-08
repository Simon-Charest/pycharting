from pathlib import Path
from sqlcipher3.dbapi2 import Connection, Cursor, connect

try: from constant import *
except ImportError: from pycharting.constant import *


BOOLEAN_KEYS: set[str] = {"accessory", "amiibo", "console", "gamepad", "previously_owned", "reproduction", "virtual", "wishlist"}
ADDED_ITEM_COLUMNS: tuple[str, ...] = ("game", "manual", "box", "paid", "pricecharting", "amiibo", "wishlist", "accessory")  # Columns that older databases lack.
ADDED_ROW_COLUMNS: tuple[str, ...] = ("accessory", "gamepad", "previously_owned", "reproduction", "virtual", "wishlist")  # Same, for spreadsheet rows.
ADDED_ROW_PRICE_COLUMNS: tuple[str, ...] = ("paid",)  # Same, for spreadsheet rows, without a type: a price can be a number or an X.
ADDED_TEXT_COLUMNS: tuple[str, ...] = ("date",)  # Columns that older databases lack, in both tables: the yyyy-mm-dd date of the Item, Manual and Box prices.


def open_database(file: Path = DATABASE_FILE, password: str = DATABASE_PASSWORD) -> Connection:
    """Open the encrypted database, failing immediately if the password is wrong."""

    if not password or file.is_dir():
        raise ValueError("DATABASE_FILE and DATABASE_PASSWORD must be set in .env (see .env.example).")

    connection: Connection = connect(file)
    escaped_password: str = password.replace("'", "''")  # PRAGMA does not support bound parameters.
    connection.execute(f"PRAGMA key = '{escaped_password}'")
    connection.execute("SELECT COUNT(1) FROM sqlite_master").fetchone()

    return connection


def ensure_collection_schema(connection: Connection) -> None:
    """Create the collection tables, and add the columns that older databases lack."""

    connection.executescript(DATABASE_PATH.joinpath("collection/create.sql").read_text())
    existing: set = {row[1] for row in connection.execute("PRAGMA table_info(collection_items)")}

    for column in ADDED_ITEM_COLUMNS:
        if column not in existing:
            connection.execute(f"ALTER TABLE collection_items ADD COLUMN {column}")

    connection.commit()

    if "quantity" not in {row[1] for row in connection.execute("PRAGMA table_info(spreadsheet_rows)")}:
        connection.executescript(DATABASE_PATH.joinpath("collection/migrate_quantity.sql").read_text())

    existing_rows: set = {row[1] for row in connection.execute("PRAGMA table_info(spreadsheet_rows)")}

    for column in ADDED_ROW_COLUMNS:
        if column not in existing_rows:
            connection.execute(f'ALTER TABLE spreadsheet_rows ADD COLUMN "{column}" INTEGER')

    for column in ADDED_ROW_PRICE_COLUMNS:
        if column not in existing_rows:
            connection.execute(f'ALTER TABLE spreadsheet_rows ADD COLUMN "{column}"')

    for column in ADDED_TEXT_COLUMNS:
        if column not in existing:
            connection.execute(f'ALTER TABLE collection_items ADD COLUMN "{column}" TEXT')

        if column not in existing_rows:
            connection.execute(f'ALTER TABLE spreadsheet_rows ADD COLUMN "{column}" TEXT')

    connection.commit()

    if "region" not in existing:
        connection.executescript(DATABASE_PATH.joinpath("collection/migrate_region_owner_source.sql").read_text())


def load_collection(connection: Connection) -> dict:
    """Load every collection item, grouped by console and merged across owners."""

    ensure_collection_schema(connection)
    rows: list = execute(connection, DATABASE_PATH.joinpath("collection/select_items.sql").read_text())
    row: dict
    data: dict = {}

    for row in rows:
        group: str = row.pop("group_name")
        item: dict = {key: bool(value) if key in BOOLEAN_KEYS else value for key, value in row.items() if value is not None}
        data.setdefault(group, []).append(item)

    return data


def get_collection_entries(connection: Connection) -> list:
    """List every collection item and spreadsheet row in a common shape for the web page."""

    ensure_collection_schema(connection)
    row: dict
    entries: list = []

    for row in execute(connection, DATABASE_PATH.joinpath("collection/select_item_entries.sql").read_text()):
        values: dict = {key: bool(row[key]) if key in BOOLEAN_KEYS and row[key] is not None else row[key] for key in row if key not in ("id", "owner", "source", "group_name", "name")}
        entries.append({"kind": "item", "id": row["id"], "owner": row["owner"], "source": row["source"], "console": row["group_name"], "title": row["name"], "values": values})

    for row in execute(connection, DATABASE_PATH.joinpath("collection/select_row_entries.sql").read_text()):
        values: dict = {key: row[key] for key in row if key not in ("id", "owner", "source", "system", "title")}

        # The spreadsheet marked its tags with an X; any value means the tag is set
        for key in BOOLEAN_KEYS:
            values[key] = True if values[key] else None

        entries.append({"kind": "row", "id": row["id"], "owner": row["owner"], "source": row["source"], "console": row["system"], "title": row["title"], "values": values})

    return entries


def get_owners(connection: Connection) -> list:
    return execute(connection, DATABASE_PATH.joinpath("collection/select_owners.sql").read_text())


def add_collection_item(connection: Connection, parameters: dict) -> bool:
    """Add an item for an owner; return False if that owner does not exist."""

    connection.execute(DATABASE_PATH.joinpath("collection/insert_added_source.sql").read_text(), parameters)
    count: int = connection.execute(DATABASE_PATH.joinpath("collection/insert_item.sql").read_text(), parameters).rowcount
    connection.commit()

    return count > 0


def get_entry_prices(connection: Connection, kind: str, id: int) -> dict | None:
    """The title, console, region, parts and PriceCharting link of an item or a spreadsheet row."""

    rows: list = execute(connection, DATABASE_PATH.joinpath(f"collection/select_{kind}_prices.sql").read_text(), {"id": id})

    return rows[0] if rows else None


def change_collection_entry(connection: Connection, script: str, parameters: dict) -> bool:
    """Run an update or delete script from db/collection; return whether an entry was affected."""

    count: int = connection.execute(DATABASE_PATH.joinpath(f"collection/{script}.sql").read_text(), parameters).rowcount
    connection.commit()

    return count > 0


def delete_game(connection: Connection, console_name: str, product_name: str) -> None:
    sql: str = DATABASE_PATH.joinpath("games/delete.sql").read_text()
    execute(connection, sql, {"console_name": console_name, "product_name": product_name})


def execute(connection: Connection, sql: str, parameters: dict | tuple = ()) -> list:
    """Run a SQL query and return its results as JSON data."""

    cursor: Cursor = connection.cursor()
    cursor.execute(sql, parameters)
    rows: list = cursor.fetchall()
    cursor.close()
    results: list = []

    if rows:
        row: tuple
        columns: list = [description[0] for description in cursor.description]

        for row in rows:
            results.append(dict(zip(columns, row)))

    else:
        connection.commit()

    return results


def get_statistical_report(connection: Connection) -> list:
    # Get data
    sql: str = DATABASE_PATH.joinpath("games/select_stats.sql").read_text()
    rows: list = execute(connection, sql)

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

    avg: float = round(sum / count, 2) if count else 0
    sum = round(sum, 2)

    # Append totals
    rows.append({"console_name": "total", "count": count, "min": min, "avg": avg, "max": max, "sum": sum})

    return rows


def get_top_report(connection: Connection, top: int) -> list:
    # Get data
    sql: str = DATABASE_PATH.joinpath("games/select_top.sql").read_text()
    rows: list = execute(connection, sql, (top,))

    # Calculate totals
    row: dict
    count: int = 0
    min: float = 0
    max: float = 0
    sum: float = 0
    
    for row in rows:
        count += 1

        if isinstance(row["loose_price"], (float, int)):
            if min == 0 or row["loose_price"] < min:
                min = row["loose_price"]

            if row["loose_price"] > max:
                max = row["loose_price"]

            sum += row["loose_price"]

    avg: float = round(sum / count, 2) if count else 0
    sum = round(sum, 2)

    # Append totals
    rows.append({"console_name": "total", "count": count, "min": min, "avg": avg, "max": max, "sum": sum})

    return rows

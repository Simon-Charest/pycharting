from pathlib import Path
from sqlcipher3.dbapi2 import Connection, Cursor, connect

from src.constant import DATABASE_FILE, DATABASE_PASSWORD, SQL_PATH


BOOLEAN_KEYS: set[str] = {"accessory", "amiibo", "console", "damaged", "selling", "gamepad", "previously_owned", "reproduction", "virtual", "wishlist"}
ADDED_ITEM_COLUMNS: tuple[str, ...] = ("game", "manual", "box", "paid", "pricecharting", "amiibo", "wishlist", "accessory", "damaged", "selling")  # Columns that older databases lack.
ADDED_ROW_COLUMNS: tuple[str, ...] = ("accessory", "damaged", "selling", "gamepad", "previously_owned", "reproduction", "virtual", "wishlist")  # Same, for spreadsheet rows.
ADDED_ROW_PRICE_COLUMNS: tuple[str, ...] = ("paid",)  # Same, for spreadsheet rows, without a type: a price can be a number or an X.
ADDED_USER_COLUMNS: tuple[str, ...] = ("first_name", "last_name")  # Same, for accounts.
RENAMED_COLUMNS: dict[str, str] = {"duplicate": "selling"}  # Old name: new name, in both tables.
ADDED_TEXT_COLUMNS: tuple[str, ...] = ("date",)  # Columns that older databases lack, in both tables: the yyyy-mm-dd date of the Item, Manual and Box prices.


def open_database(file: Path = DATABASE_FILE, password: str = DATABASE_PASSWORD) -> Connection:
    """Open the encrypted database, failing immediately if the password is wrong."""

    if not password or file.is_dir():
        raise ValueError("DATABASE_FILE and DATABASE_PASSWORD must be set in .env (see .env.example).")

    connection: Connection = connect(file, check_same_thread=False)  # Every query runs on the server's one event loop; tests drive it from another thread
    escaped_password: str = password.replace("'", "''")  # PRAGMA does not support bound parameters.
    connection.execute(f"PRAGMA key = '{escaped_password}'")
    connection.execute("SELECT COUNT(1) FROM sqlite_master").fetchone()

    return connection


def backup_database(connection: Connection, file: Path, password: str = DATABASE_PASSWORD) -> None:
    """Write a consistent copy of the whole database, encrypted with the same password, even while the site runs."""

    file.unlink(missing_ok=True)
    escaped_file: str = str(file).replace("'", "''")  # ATTACH does not support bound parameters for the key.
    escaped_password: str = password.replace("'", "''")
    connection.execute(f"ATTACH DATABASE '{escaped_file}' AS backup KEY '{escaped_password}'")

    try:
        connection.execute("SELECT sqlcipher_export('backup')")
    finally:
        connection.execute("DETACH DATABASE backup")


def ensure_collection_schema(connection: Connection) -> None:
    """Create the collection tables, and add the columns that older databases lack."""

    connection.executescript(SQL_PATH.joinpath("create.sql").read_text())

    # Renamed tags keep their values; done before the missing columns are added, so the new name is not created empty
    for table in ("collection_items", "spreadsheet_rows"):
        columns: set = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}

        for old, new in RENAMED_COLUMNS.items():
            if old in columns and new not in columns:
                connection.execute(f'ALTER TABLE {table} RENAME COLUMN "{old}" TO "{new}"')

    existing_users: set = {row[1] for row in connection.execute("PRAGMA table_info(users)")}

    for column in ADDED_USER_COLUMNS:
        if column not in existing_users:
            connection.execute(f'ALTER TABLE users ADD COLUMN "{column}" TEXT')
    existing: set = {row[1] for row in connection.execute("PRAGMA table_info(collection_items)")}

    for column in ADDED_ITEM_COLUMNS:
        if column not in existing:
            connection.execute(f"ALTER TABLE collection_items ADD COLUMN {column}")

    connection.commit()

    if "quantity" not in {row[1] for row in connection.execute("PRAGMA table_info(spreadsheet_rows)")}:
        connection.executescript(SQL_PATH.joinpath("migrate_quantity.sql").read_text())

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
        connection.executescript(SQL_PATH.joinpath("migrate_region_owner_source.sql").read_text())


def get_collection_entries(connection: Connection) -> list:
    """List every collection item and spreadsheet row in a common shape for the web page."""

    ensure_collection_schema(connection)
    row: dict
    entries: list = []

    for row in execute(connection, SQL_PATH.joinpath("select_item_entries.sql").read_text()):
        values: dict = {key: bool(row[key]) if key in BOOLEAN_KEYS and row[key] is not None else row[key] for key in row if key not in ("id", "owner", "source", "group_name", "name")}
        entries.append({"kind": "item", "id": row["id"], "owner": row["owner"], "source": row["source"], "console": row["group_name"], "title": row["name"], "values": values})

    for row in execute(connection, SQL_PATH.joinpath("select_row_entries.sql").read_text()):
        values: dict = {key: row[key] for key in row if key not in ("id", "owner", "source", "system", "title")}

        # The spreadsheet marked its tags with an X; any value means the tag is set
        for key in BOOLEAN_KEYS:
            values[key] = True if values[key] else None

        entries.append({"kind": "row", "id": row["id"], "owner": row["owner"], "source": row["source"], "console": row["system"], "title": row["title"], "values": values})

    return entries


def get_owners(connection: Connection) -> list:
    return execute(connection, SQL_PATH.joinpath("select_owners.sql").read_text())


def add_collection_item(connection: Connection, parameters: dict) -> bool:
    """Add an item for an owner; return False if that owner does not exist."""

    connection.execute(SQL_PATH.joinpath("insert_added_source.sql").read_text(), parameters)
    count: int = connection.execute(SQL_PATH.joinpath("insert_item.sql").read_text(), parameters).rowcount
    connection.commit()

    return count > 0


def get_entry_prices(connection: Connection, kind: str, id: int) -> dict | None:
    """The title, console, region, parts and PriceCharting link of an item or a spreadsheet row."""

    rows: list = execute(connection, SQL_PATH.joinpath(f"select_{kind}_prices.sql").read_text(), {"id": id})

    return rows[0] if rows else None


def get_user(connection: Connection, username: str) -> dict | None:
    """The account with that name, whatever its case, with its password hash."""

    rows: list = execute(connection, SQL_PATH.joinpath("select_user.sql").read_text(), {"username": username})

    return rows[0] if rows else None


def add_user(connection: Connection, username: str, password_hash: str, role: str, first_name: str | None = None, last_name: str | None = None) -> bool:
    """Add an account; return False if that name is already taken."""

    parameters: dict = {"username": username, "password_hash": password_hash, "role": role, "first_name": first_name, "last_name": last_name}
    count: int = connection.execute(SQL_PATH.joinpath("insert_user.sql").read_text(), parameters).rowcount
    connection.commit()

    return count > 0


def set_user_password(connection: Connection, username: str, password_hash: str) -> bool:
    """Replace an account's password; return False if there is no such account."""

    count: int = connection.execute(SQL_PATH.joinpath("update_user_password.sql").read_text(), {"username": username, "password_hash": password_hash}).rowcount
    connection.commit()

    return count > 0


def set_user_role(connection: Connection, username: str, role: str) -> bool:
    """Make an account an administrator or a collaborator; return False if there is no such account."""

    count: int = connection.execute(SQL_PATH.joinpath("update_user_role.sql").read_text(), {"username": username, "role": role}).rowcount
    connection.commit()

    return count > 0


def get_users(connection: Connection) -> list:
    """Every account, by name, without its password hash."""

    return execute(connection, SQL_PATH.joinpath("select_users.sql").read_text())


def update_user(connection: Connection, id: int, role: str | None, password_hash: str | None, names: tuple | None = None) -> bool:
    """Change an account's role, password and/or (first name, last name); return False if there is no such account."""

    first_name, last_name = names or (None, None)
    parameters: dict = {"id": id, "role": role, "password_hash": password_hash, "set_names": names is not None, "first_name": first_name, "last_name": last_name}
    count: int = connection.execute(SQL_PATH.joinpath("update_user.sql").read_text(), parameters).rowcount
    connection.commit()

    return count > 0


def delete_user(connection: Connection, id: int) -> bool:
    """Delete an account and sign it out everywhere; return False if there is no such account."""

    connection.execute(SQL_PATH.joinpath("delete_user_sessions.sql").read_text(), {"id": id})
    count: int = connection.execute(SQL_PATH.joinpath("delete_user.sql").read_text(), {"id": id}).rowcount
    connection.commit()

    return count > 0


def delete_user_sessions(connection: Connection, id: int) -> None:
    connection.execute(SQL_PATH.joinpath("delete_user_sessions.sql").read_text(), {"id": id})
    connection.commit()


def add_session(connection: Connection, token_hash: str, user_id: int, days: int) -> None:
    """Remember a signed-in browser, and forget the sessions that have expired."""

    connection.execute(SQL_PATH.joinpath("delete_expired_sessions.sql").read_text())
    connection.execute(SQL_PATH.joinpath("insert_session.sql").read_text(), {"token_hash": token_hash, "user_id": user_id, "days": days})
    connection.commit()


def get_session_user(connection: Connection, token_hash: str) -> dict | None:
    """The name and role of the account of a session that has not expired."""

    rows: list = execute(connection, SQL_PATH.joinpath("select_session_user.sql").read_text(), {"token_hash": token_hash})

    return rows[0] if rows else None


def delete_session(connection: Connection, token_hash: str) -> None:
    connection.execute(SQL_PATH.joinpath("delete_session.sql").read_text(), {"token_hash": token_hash})
    connection.commit()


def change_collection_entry(connection: Connection, script: str, parameters: dict) -> bool:
    """Run an update or delete script from db/collection; return whether an entry was affected."""

    count: int = connection.execute(SQL_PATH.joinpath(f"{script}.sql").read_text(), parameters).rowcount
    connection.commit()

    return count > 0


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

from sqlite3 import Connection, Cursor

from constant import *


def execute(connection: Connection, sql: str) -> list:
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

    avg: float = round(sum / count, 2)
    sum = round(sum, 2)

    # Append totals
    rows.append({"console_name": "total", "count": count, "min": min, "avg": avg, "max": max, "sum": sum})

    return rows


def get_top_report(connection: Connection, top: str) -> list:
    # Get data
    sql: str = DATABASE_PATH.joinpath("games/select_top.sql").read_text()
    rows: list = execute(connection, sql.replace("?", top))

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

        avg: float = round(sum / count, 2)
        sum = round(sum, 2)

    # Append totals
    rows.append({"console_name": "total", "count": count, "min": min, "avg": avg, "max": max, "sum": sum})

    return rows

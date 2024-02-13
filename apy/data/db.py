from pathlib import Path
from sqlite3 import connect, Connection


def init_users(connection: Connection = None) -> str:
    message: str

    try:
        if not connection:
            connection = connect(Path(__file__).parent.joinpath("apy.db"))
            
        drop_users(connection)
        create_users(connection)
        users: list = [
            ("John", "Doe", "john@example.com"),
            ("Jane", "Smith", "jane@example.com")
        ]
        insert_users(connection, users)
        message = {"message": "Database initialized."}

    except Exception as exception:
        message = {"error": exception}

    finally:
        return message


def drop_users(connection: Connection) -> None:
    sql: str = Path(__file__).parent.joinpath("users/drop.sql").read_text()
    connection.cursor().execute(sql)


def create_users(connection: Connection) -> None:
    sql: str = Path(__file__).parent.joinpath("users/create.sql").read_text()
    connection.cursor().execute(sql)


def select_users(connection: Connection) -> list:
    sql: str = Path(__file__).parent.joinpath("users/select.sql").read_text()
    rows: list = connection.cursor().execute(sql).fetchall()

    return rows


def insert_users(connection: Connection, users: list):
    sql: str = Path(__file__).parent.joinpath("users/insert.sql").read_text()
    connection.cursor().executemany(sql, users)
    connection.commit()


def update_users(connection: Connection, users: list):
    sql: str = Path(__file__).parent.joinpath("users/update.sql").read_text()
    connection.cursor().executemany(sql, users)
    connection.commit()


def delete_users(connection: Connection, id: str) -> None:
    sql: str = Path(__file__).parent.joinpath("users/delete.sql").read_text()
    connection.cursor().execute(sql, id)
    connection.commit()


if __name__ == "__main__":  
    init_users()

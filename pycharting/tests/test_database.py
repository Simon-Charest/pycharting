from pathlib import Path
from pytest import raises
from sqlcipher3.dbapi2 import Connection, DatabaseError

from pycharting.constant import DATABASE_PATH
from pycharting.database import delete_game,get_statistical_report, get_top_report, load_collection, open_database


PASSWORD: str = "it's a secret"


def _create_database(file: Path) -> None:
    connection: Connection = open_database(file, PASSWORD)
    load_collection(connection)
    connection.execute("INSERT INTO owners (id, name) VALUES (1, 'A'), (2, 'B')")
    connection.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x''), (2, 2, 'b', '', x'')")
    connection.executemany(
        "INSERT INTO collection_items (source_file_id, position, group_name, name, console, game) VALUES (?, ?, ?, ?, ?, ?)",
        [(1, 0, "Wii", "Wii Console", 1, 99.5), (2, 0, "Wii", "Zelda", None, None)]
    )
    connection.commit()
    connection.close()


def _create_games(file: Path, prices: list) -> Connection:
    connection: Connection = open_database(file, PASSWORD)
    connection.execute(DATABASE_PATH.joinpath("games/create.sql").read_text())
    connection.executemany(
        "INSERT INTO games (console_name, id, product_name, loose_price, moment) VALUES ('wii', ?, ?, ?, DATETIME('NOW', 'LOCALTIME'))",
        [(index, f"game-{index}", price) for index, price in enumerate(prices)]
    )
    connection.commit()

    return connection


class TestDatabase:
    def test_file_is_encrypted(self, tmp_path: Path) -> None:
        # Arrange
        file: Path = tmp_path.joinpath("test.sqlite")

        # Act
        _create_database(file)

        # Assert
        assert not file.read_bytes().startswith(b"SQLite format 3")

    def test_wrong_password_is_rejected(self, tmp_path: Path) -> None:
        # Arrange
        file: Path = tmp_path.joinpath("test.sqlite")
        _create_database(file)

        # Act and assert
        with raises(DatabaseError):
            open_database(file, "wrong")

    def test_missing_password_is_rejected(self, tmp_path: Path) -> None:
        # Act and assert
        with raises(ValueError):
            open_database(tmp_path.joinpath("test.sqlite"), "")

    def test_load_collection_merges_owners_and_restores_types(self, tmp_path: Path) -> None:
        # Arrange
        file: Path = tmp_path.joinpath("test.sqlite")
        _create_database(file)
        expected: dict = {"Wii": [{"name": "Wii Console", "console": True}, {"name": "Zelda"}]}

        # Act
        connection: Connection = open_database(file, PASSWORD)
        actual: dict = load_collection(connection)
        connection.close()

        # Assert
        assert expected == actual

    def test_top_report_limits_rows_and_totals_them(self, tmp_path: Path) -> None:
        # Arrange
        connection: Connection = _create_games(tmp_path.joinpath("test.sqlite"), [10.004, 20.004, 5.0])

        # Act
        actual: list = get_top_report(connection, 2)
        connection.close()

        # Assert
        assert ["game-1", "game-0"] == [row["product_name"] for row in actual[:-1]]
        assert {"console_name": "total", "count": 2, "min": 10.004, "avg": 15.0, "max": 20.004, "sum": 30.01} == actual[-1]

    def test_reports_without_prices_do_not_fail(self, tmp_path: Path) -> None:
        # Arrange
        connection: Connection = _create_games(tmp_path.joinpath("test.sqlite"), [])
        connection.execute(DATABASE_PATH.joinpath("games/create.sql").read_text())
        expected: list = [{"console_name": "total", "count": 0, "min": 0, "avg": 0, "max": 0, "sum": 0}]

        # Act and assert
        assert expected == get_top_report(connection, 5)
        assert expected == get_statistical_report(connection)
        connection.close()

    def test_delete_game_treats_names_as_values(self, tmp_path: Path) -> None:
        # Arrange
        connection: Connection = _create_games(tmp_path.joinpath("test.sqlite"), [1.0, 2.0])

        # Act
        delete_game(connection, "wii", "x' OR '1'='1")
        unchanged: int = connection.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        delete_game(connection, "wii", "game-0")
        remaining: int = connection.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        connection.close()

        # Assert
        assert (2, 1) == (unchanged, remaining)

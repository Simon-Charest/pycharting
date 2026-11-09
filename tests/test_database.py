from pathlib import Path
from pytest import raises
from sqlcipher3.dbapi2 import Connection, DatabaseError

from src.database import ensure_collection_schema, open_database


PASSWORD: str = "it's a secret"


def _create_database(file: Path) -> None:
    connection: Connection = open_database(file, PASSWORD)
    ensure_collection_schema(connection)
    connection.execute("INSERT INTO owners (id, name) VALUES (1, 'A'), (2, 'B')")
    connection.execute("INSERT INTO source_files (id, owner_id, path, sha256, content) VALUES (1, 1, 'a', '', x''), (2, 2, 'b', '', x'')")
    connection.executemany(
        "INSERT INTO collection_items (source_file_id, position, group_name, name, console, game) VALUES (?, ?, ?, ?, ?, ?)",
        [(1, 0, "Wii", "Wii Console", 1, 99.5), (2, 0, "Wii", "Zelda", None, None)]
    )
    connection.commit()
    connection.close()


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

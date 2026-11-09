from pathlib import Path
from pytest import raises
from sqlcipher3.dbapi2 import Connection, DatabaseError

from src.database import backup_database, ensure_collection_schema, open_database


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

    def test_backup_is_a_full_encrypted_copy(self, tmp_path: Path) -> None:
        # Arrange
        source: Path = tmp_path.joinpath("test.sqlite")
        copy: Path = tmp_path.joinpath("copy.sqlite")
        _create_database(source)
        copy.write_bytes(b"an older copy, replaced")
        connection: Connection = open_database(source, PASSWORD)

        # Act
        backup_database(connection, copy, PASSWORD)
        connection.close()
        restored: Connection = open_database(copy, PASSWORD)
        names: list = [row[0] for row in restored.execute("SELECT name FROM collection_items ORDER BY name")]
        restored.close()

        # Assert
        assert names == ["Wii Console", "Zelda"]
        assert not copy.read_bytes().startswith(b"SQLite format 3")
        with raises(DatabaseError):
            open_database(copy, "wrong")
